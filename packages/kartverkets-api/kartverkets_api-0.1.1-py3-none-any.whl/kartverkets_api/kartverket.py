import os
import zeep
import requests
from zeep import Settings,AsyncClient,Client
from zeep.transports import Transport
from requests import Session
from requests.auth import HTTPBasicAuth
from zeep.helpers import serialize_object
from zeep.plugins import HistoryPlugin
from dotenv import load_dotenv
from settings import *
import pandas as pd
import logging
from typing import Literal
from zeep.transports import AsyncTransport
import httpx
from sibr_module import BigQuery,Logger
import asyncio
from datetime import datetime
from urllib.parse import quote_plus
from lxml import etree # <--- LEGG TIL DENNE LINJEN
from sibr_api import ApiBase

load_dotenv()


class CustomAsyncTransport(AsyncTransport):
    def __init__(self, client=None, wsdl_client=None, cache=None, timeout=300, operation_timeout=300, verify_ssl=True, proxy=None):
        self._close_session = bool(client is None)
        self.cache = cache
        # Initialiser wsdl_client uten proxies-argumentet
        self.wsdl_client = wsdl_client or httpx.Client(
            verify=verify_ssl,
            timeout=timeout,
        )
        self.client = client or httpx.AsyncClient(
            verify=verify_ssl,
            timeout=operation_timeout,
        )
        self.logger = logging.getLogger(__name__)

class kartverketsAPI:
    def __init__(self, logger: Logger = None):
        if logger is None:
            logger = Logger("KartverketAPI")
        self.logger = logger
        self.username = os.getenv("GRUNNBOK_USERNAME")
        self.password = os.getenv("GRUNNBOK_PASSWORD")

        self.settings = Settings(strict=False, xml_huge_tree=True)
        self.transport = None
        self.session = None

        self.httpx_client = None
        self.async_transport = None
        self.timeout_seconds = 60

        self.base_url = "https://www.grunnbok.no/grunnbok/wsapi/v2/"
        self.services = {
            "GrunnboksutskriftService": f"{self.base_url}GrunnboksutskriftServiceWS?WSDL",
            "RegisterenhetService": f"{self.base_url}RegisterenhetServiceWS?WSDL",
            "RettsstiftelseService": f"{self.base_url}RettsstiftelseServiceWS?WSDL",
            "InformasjonService": f"{self.base_url}InformasjonServiceWS?WSDL",
            "EndringsloggService": f"{self.base_url}EndringsloggServiceWS?WSDL",
            "NedlastningService": f"{self.base_url}NedlastningServiceWS?WSDL",
            "KodelisteService": f"{self.base_url}KodelisteServiceWS?WSDL",
            "IdentService": f"{self.base_url}IdentServiceWS?WSDL",
            "KommuneService": f"{self.base_url}KommuneServiceWS?WSDL",
            "PersonService": f"{self.base_url}PersonServiceWS?WSDL",

            # Tjenester for innsending og validering
            "InnsendingService": f"{self.base_url}InnsendingServiceWS?WSDL",
            "ValideringService": f"{self.base_url}ValideringServiceWS?WSDL",

            # Andre spesialiserte tjenester
            "StoreService": f"{self.base_url}StoreServiceWS?WSDL",
            "RettsstiftelsestypebegrensningService": f"{self.base_url}RettsstiftelsestypebegrensningServiceWS?WSDL",
            "RegisterenhetsrettsandelService": f"{self.base_url}RegisterenhetsrettsandelServiceWS?WSDL",
            "RegisterenhetsrettService": f"{self.base_url}RegisterenhetsrettServiceWS?WSDL",
            "SeksjonssameieandelService": f"{self.base_url}SeksjonssameieandelServiceWS?WSDL",
            "OverfoeringService": f"{self.base_url}OverfoeringServiceWS?WSDL",
            "RegistreringsstatusService": f"{self.base_url}RegistreringsstatusServiceWS?WSDL",
            "ForeloepigRegistreringService": f"{self.base_url}ForeloepigRegistreringServiceWS?WSDL"
        }
        self.context = self._create_context()

    def _create_context(self):
        ident_service_wsdl = self.services['IdentService']
        with requests.Session() as session:
            session.auth = HTTPBasicAuth(self.username, self.password)
            transport = Transport(session=session)
            ident_client = Client(wsdl=ident_service_wsdl, transport=transport)
            GrunnbokContext = ident_client.get_type('ns1:GrunnbokContext')
            Timestamp = ident_client.get_type('ns1:Timestamp')
            return GrunnbokContext(
                clientIdentification="sibr-python-test",
                systemVersion="v2",
                snapshotVersion=Timestamp('9999-01-01T00:00:00+01:00'),
                locale="nb_NO"
            )

    async def close(self):
        if self.httpx_client and not self.httpx_client.is_closed:
            await self.httpx_client.aclose()
            self.logger.info("Asynkron sesjon er lukket.")

    async def _init_async_transport(self):
        if self.httpx_client is None:
            auth = httpx.BasicAuth(self.username, self.password)
            self.httpx_client = httpx.AsyncClient(auth=auth,timeout=self.timeout_seconds)
            # Vi sender vår egen klient inn til AsyncTransport
            # self.async_transport = AsyncTransport(client=self.httpx_client, cache=None)
            self.async_transport = CustomAsyncTransport(self.httpx_client)
            self.logger.info("Async transport initiated")

    def _init_transport(self):
        if self.session is None and self.transport is None:
            self.session = Session()
            self.session.auth = HTTPBasicAuth(self.username, self.password)
            self.transport = Transport(session=self.session)

    def _get_prefix_for_uri(self, client, target_uri):
        for prefix, uri in client.namespaces.items():
            if uri == target_uri:
                return prefix
        raise ValueError(f"Ingen prefix funnet for URI: {target_uri}. Sjekk namespaces-print.")

    def _ensure_col_names(self, col_names: list[str]):
        new_col_names = []
        for col_name in col_names:
            new_col_names.append(
                col_name.strip().lower().replace(' ', '_').replace('-', '_').replace(".", "_").replace("ø",
                                                                                                       "o").replace("æ",
                                                                                                                    "a").replace(
                    "å", "a"))
        return new_col_names

    def explore_type(self, type_object):
        """
        En enkel og robust funksjon som viser feltene til en datatype
        ved å serialisere et tomt objekt.
        """
        # ENDRINGEN ER HER: Bytter fra __name__ til .name
        print(f"\n--- Undersøker datatypen '{type_object.name}' ---")

        empty_instance = type_object()
        fields = serialize_object(empty_instance)

        # For en simpel type som MatrikkelenhetId, vil 'fields' være None.
        if fields is None:
            print("Dette er en simpel type (f.eks. en streng) som lages med én enkelt verdi.")
        else:
            print("Dette er en kompleks type med følgende felter:")
            for field_name in fields.keys():
                print(f"  - '{field_name}'")

    def _get_propertyIds(self, properties: list[dict],ownership_type : Literal["eier","andel"] = "eier") -> list[tuple]:
        """

        :param properties: properties will have to be in format of dictionaries with keys in
        ['kommunenummer', 'gaardsnummer', 'bruksnummer', 'festenummer', 'seksjonsnummer']
        :return: a unique property id 'RegisterenhetId' from kartverket

        example_input:
        property = {
                    "kommunenummer" : "3212",
                    "gaardsnummer" : 1,
                    "bruksnummer" : 5,
                    "festenummer": 0,
                    "seksjonsnummer": 0
                    }
        """
        self._init_transport()
        ident_service_wsdl = self.services.get('IdentService')
        ident_client = zeep.Client(wsdl=ident_service_wsdl, transport=self.transport, settings=self.settings)
        ident_client.plugins = [HistoryPlugin()]

        factory = ident_client.type_factory('ns16')  # Namespace for grunnboksidenter (juster etter WSDL)
        idents = {'item': []}
        for prop in properties:
            if ownership_type == "eier":
                prop_ident = factory.MatrikkelenhetIdent(**prop)
            elif ownership_type == "andel":
                prop_ident = factory.BorettslagsandelIdent(**prop)
            else:
                raise TypeError(f'Expected "eier" or "andel", but got {ownership_type}')
            idents['item'].append(prop_ident)

        try:
            id_map = ident_client.service.findRegisterenhetIdsForIdents(
                grunnbokContext=self.context,
                idents=idents
            )
            #print(id_map)
            internal_ids = [(dict(id_entry.get("key")), id_entry.get("value").get("value")) for id_entry in serialize_object(id_map) if id_entry.get("value") is not None]
            self.logger.info(f"🔢  Fetched {len(internal_ids)} id's from {len(properties)} properties")
            return internal_ids
        except Exception as e:
            self.logger.error(f"Feil i batch-ID-henting: {str(e)}")
            return []

    async def _get_single_transId_by_propertyId(self, client, id,transfer_type : Literal["active","historical"] = "active"):
        #try:
        if transfer_type == "active":
            overdragelser_map = await client.service.findOverdragelserMedAktiveAndelerIRegisterenhet(
                grunnbokContext=self.context,
                registerenhetId=id
            )
            return overdragelser_map
        elif transfer_type == "historical":
            overdragelser_map = await client.service.findOverdragelserMedHistoriskeAndelerIRegisterenhet(
                grunnbokContext=self.context,
                registerenhetId=id
            )
            return overdragelser_map
        # except Exception as e:
        #     self.logger.error(f"Error fetching {id}: {str(e)}")
        #     #raise

    async def _get_transferIds_by_propertyIds(self, ids: list[str], transfer_type : Literal["active","historical"] = "active",):
        start = datetime.now()
        await self._init_async_transport()
        rettsstiftelse_wsdl = self.services.get("RettsstiftelseService")
        rettsstiftelse_client = AsyncClient(wsdl=rettsstiftelse_wsdl, transport=self.async_transport,
                                            settings=self.settings)
        rettsstiftelse_client.plugins = [HistoryPlugin()]
        self.logger.info(f"✅ Connection to Api url is ready. url {rettsstiftelse_wsdl}")

        reg_uri = 'http://kartverket.no/grunnbok/wsapi/v2/domain/register/registerenhet'
        reg_prefix = self._get_prefix_for_uri(rettsstiftelse_client, reg_uri)
        reg_factory = rettsstiftelse_client.type_factory(reg_prefix)

        try:

            registerenhet_ids = [reg_factory.RegisterenhetId(value=id_str) for id_str in ids]

            semaphore = asyncio.Semaphore(20)

            async def exe_async(reg_id):
                async with semaphore:
                    try:
                        id_str = serialize_object(reg_id).get("value")
                        result = await self._get_single_transId_by_propertyId(rettsstiftelse_client, reg_id, transfer_type)
                        return (id_str, result)
                    except zeep.exceptions.Fault as e:
                        self.logger.error(f"SOAP-feil: {e.message}")
                        # Hent ut 'envelope'-objektet og konverter det til en lesbar streng
                        sent_xml_obj = rettsstiftelse_client.plugins[0].last_sent['envelope']
                        sent_xml_str = etree.tostring(sent_xml_obj, pretty_print=True).decode('utf-8')
                        self.logger.error(f"Sent XML:\n{sent_xml_str}")  # <--- FIKSEN
                        return (id_str, None)
                    except ValueError as e:
                        self.logger.error(f"ValueError fetching {id_str}: {str(e)}")
                        raise
                    except Exception as e:
                        self.logger.error(f"Error fetching {id_str}: {str(e)}. Returning {(id_str, None)}")
                        return (id_str, None)

            tasks = [exe_async(reg_id = reg_id) for reg_id in registerenhet_ids]

            results_map = {}
            for i,future in enumerate(asyncio.as_completed(tasks)):
                id_str, output = await future
                if i % 5000 == 0:
                    self.logger.info(f'\tProcessing the {i}th item, id: {id_str}')
                if output:
                    overdragelse_ids = [item.value.value for item in output]
                    andel_ids = [item.key.value for item in output]
                    results_map[id_str] = {"overdragelse_ids": overdragelse_ids, "andel_ids": andel_ids}
                else:
                    results_map[id_str] = {"overdragelse_ids": [], "andel_ids": []}
            self.logger.info(f'🔗  Fetched {len(results_map)} transfer ids from {len(ids)} ids in {datetime.now()-start}')
            return results_map
        except zeep.exceptions.Fault as e:
            pass
            #raise
        except ValueError as ve:
            self.logger.error(f"Namespace-feil: {ve}")
            raise
        except Exception as e:
            self.logger.error(f"Annen feil: {str(e)}")
            return {}

    def _get_transferIds_by_period(self, fra_dato: str, til_dato: str, rettstype_koder: list[int] = [18]):
        # if self.session is None or self.transport is None:
        start = datetime.now()
        self._init_transport()
        rettsstiftelse_wsdl = self.services.get('RettsstiftelseService')
        rettsstiftelse_client = zeep.Client(wsdl=rettsstiftelse_wsdl, transport=self.transport, settings=self.settings)
        self.logger.info(f"✅ Tilkobling til Api url er klar. url {rettsstiftelse_wsdl}")

        bas_factory = rettsstiftelse_client.type_factory('ns1')  # basistyper
        kod_factory = rettsstiftelse_client.type_factory('ns3')  # koder
        timestamp_type = bas_factory.Timestamp
        kode_ids = {'item': [kod_factory.RettstypeKodeId(value=kode) for kode in rettstype_koder]}

        overdragelse_ids = rettsstiftelse_client.service.findOverdragelserForPeriode(
            grunnbokContext=self.context,
            rettstypeKodeIds=kode_ids,
            fraOgMedDato=timestamp_type(fra_dato + 'T00:00:00+01:00'),
            tilOgMedDato=timestamp_type(til_dato + 'T00:00:00+01:00')
        )
        obj = serialize_object(overdragelse_ids)
        self.logger.info(f"📅  Fetched {len(obj)} objects for period {fra_dato} - {til_dato} with rettstype_koder {rettstype_koder} in {datetime.now()-start}")
        return [o.get("value") for o in obj]

    def _get_info_by_transferIds(self, overdragelse_ids: list[str]):
        # if self.session is None or self.transport is None:
        start = datetime.now()
        self._init_transport()
        store_wsdl = self.services.get('StoreService')
        store_client = zeep.Client(wsdl=store_wsdl, transport=self.transport, settings=self.settings)
        self.logger.info(f"✅ Connection to Api url is ready. url {store_wsdl}")
        ret_factory = store_client.type_factory('http://kartverket.no/grunnbok/wsapi/v2/domain/register/rettsstiftelse')
        store_ids = {
            'item': [ret_factory.RettsstiftelseId(value=oid) for oid in overdragelse_ids if oid]
        }

        try:
            objects = store_client.service.getObjects(
                grunnbokContext=self.context,
                ids=store_ids
            )
            self.logger.info(f"ℹ️  Fetched {len(objects)} info objects from {len(overdragelse_ids)} transfer ids in {datetime.now() - start}")
            return objects
        except zeep.exceptions.Fault as e:
            self.logger.error(f"SOAP-error in getObjects: {e.message}")
            self.logger.error(
                f"Sent XML:\n {store_client.plugins[0].last_sent if store_client.plugins else 'No history'}")
            return []
        except Exception as e:
            self.logger.error(f"Other error in getObjects: {str(e)}")
            return []

    def _get_info_by_docId(self, doc_ids: list) -> dict:
        start = datetime.now()
        store_wsdl = self.services.get('StoreService')
        store_client = zeep.Client(wsdl=store_wsdl, transport=self.transport, settings=self.settings)
        doc_factory = store_client.type_factory('http://kartverket.no/grunnbok/wsapi/v2/domain/register/dokument')

        store_ids = {
            'item': [doc_factory.DokumentId(value=doc_id) for doc_id in doc_ids],
        }
        doc_objects = store_client.service.getObjects(
            grunnbokContext=self.context,
            ids=store_ids)

        document_map = {doc.id.value: doc for doc in doc_objects}
        transfer_date = {}
        for key, val in document_map.items():
            val = serialize_object(val)
            transfer_date[key] = val.get("registreringstidspunkt").get("timestamp")
        self.logger.info(f'📅  Fetched {len(transfer_date)} transfer dates from {len(doc_ids)} transfer ids in {datetime.now() - start}')
        return transfer_date

    def _object_to_dataframe(self, objects: list[dict],property_map = None) -> pd.DataFrame:
        """
        A function to create output as a dataframe.

        Args:
            objects (list[dict]): The list of objects to convert.
            property_map (dict): Optional. A map of property ids to transfer ids (id_value is transfer_id)

        Example:
            property_map = {'3609928': {'overdragelse_ids': ['141662867', '141662867'],
                                          'andel_ids': ['121963093', '121963094']},
                             '1414777': {'overdragelse_ids': ['130621092'], 'andel_ids': ['110439107']},
                             '806212466': {'overdragelse_ids': [], 'andel_ids': []}}
        """
        start = datetime.now()
        df = pd.json_normalize(serialize_object(objects))
        df.columns = self._ensure_col_names(df.columns)
        if property_map:
            count = 0
            for prop, ids in property_map.items():
                if count % 5000 == 0:
                    self.logger.debug(f"Matched 5000 objects. ID no.: {ids}")
                count += 1
                for id in ids.get("overdragelse_ids"):
                    df.loc[df["id_value"] == id, "property_id"] = prop
        self.logger.info(f"📊  Transformed {len(objects)} object to dataframe with shape: {df.shape} in {datetime.now() - start}")
        return df

    async def get_by_property(self, properties: list[dict], transfer_type : Literal["active","historical"] = "active",ownership_type : Literal["eier","andel"] = "eier"):
        starttime = datetime.now()
        #GET PROPERTY IDS
        self.logger.info(f'🔢  Fetching property ids for {len(properties)} properties with ownership type {ownership_type}')
        ids = self._get_propertyIds(properties,ownership_type=ownership_type)
        prop_dict = {}
        for id_tuple in ids:
            prop, id_val = id_tuple
            prop_dict[id_val] = prop
        props_df = pd.DataFrame.from_dict(prop_dict, orient='index').reset_index().rename(columns= {"index" : "property_id"})

        #GET TRANSFER IDS
        self.logger.info(f'🔗  Fetching transfer ids for {len(ids)} properties with transfer type {transfer_type}')
        trans_id_prop = await self._get_transferIds_by_propertyIds(ids = list(prop_dict.keys()), transfer_type=transfer_type)
        overdragelse_ids = []
        for _, val in trans_id_prop.items():
            val.get("overdragelse_ids")
            overdragelse_ids.extend(val.get("overdragelse_ids"))

        #GET INFO FROM EACH TRANSFER ID
        self.logger.info(f'ℹ️  Fetching info for {len(overdragelse_ids)} transfers')
        objects = self._get_info_by_transferIds(overdragelse_ids)

        #GET INFO BY DOCID
        doc_ids = []
        for e in serialize_object(objects):
            doc_ids.append(e.get("dokumentId").get("value"))
        self.logger.info(f'📅  Fetching tranfer dates for {len(doc_ids)} transfers')
        transfer_date = self._get_info_by_docId(doc_ids)

        #MAKE OUTOUT
        self.logger.info(f'📊  Transforming the output')
        df_raw = self._object_to_dataframe(objects=objects,property_map=trans_id_prop)
        if "property_id" in df_raw.columns and "property_id" in props_df.columns:
            df = pd.merge(df_raw, props_df, on="property_id", how="left")
        else:
            raise ValueError(f'property_id missing in one of the dataframes')

        if "dokumentid_value" in df.columns:
            df["registreringstidspunkt"] = df["dokumentid_value"].map(transfer_date)
            df["registreringstidspunkt"] = pd.to_datetime(df["registreringstidspunkt"], utc=True)
        else:
            raise ValueError(f'dokumentid_value not in dataframe')
        self.logger.info(f'Getting {len(df)} successful results from {len(properties)} in total time: {datetime.now() - starttime}.')
        return df

    def get_by_period(self, start_date: str, end_date: str, property_types: list = [18, 116], saver = None):
        #GET TRANSFER IDS
        ids = self._get_transferIds_by_period(start_date, end_date, property_types)

        #GET INFO BY TRANSFER IDS
        objects = self._get_info_by_transferIds(ids)

        # GET INFO BY DOCID
        doc_ids = []
        for e in serialize_object(objects):
            doc_ids.append(e.get("dokumentId").get("value"))
        transfer_date = self._get_info_by_docId(doc_ids)

        #MAKE OUTPUT
        df = self._object_to_dataframe(objects)
        if "dokumentid_value" in df.columns:
            df["registreringstidspunkt"] = df["dokumentid_value"].map(transfer_date)
        else:
            raise ValueError(f'dokumentid_value not in dataframe')
        return df
