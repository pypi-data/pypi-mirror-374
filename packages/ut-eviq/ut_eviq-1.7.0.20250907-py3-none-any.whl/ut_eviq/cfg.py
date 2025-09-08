"""
This module provides utility classes for the management of OmniTracker
EcoVadis NHRR (Nachhaltigkeits Risiko Rating) processing for Department UMH
"""
from typing import Any

from ut_eviq.rst.taskioc import TaskIoc as EviqRstTaskIoc
from ut_eviq.xls.taskioc import TaskIoc as EviqXlsTaskIoc

from ut_dic.dic import Dic


TyDic = dict[Any, Any]


class Cfg:

    _DoC = None
    _Utils = None
    eviq_lang = 'De'
    eviq_if = 'xls'

    Url = {

        'd_sandbox': {
            'url': 'https://api-sandboc.ecovadis-survey.com',
            'description': 'Used to test the API calls in a dummy database',
        },
        'd_live': {
            'url': 'https://api.ecovadis-survey.com',
            'description': 'Set calls here to interact with live data',
        },
        'version': 'v2.2',
    }

    Request = {

        'post_token': {
            'command':  'POST',
            'endpoint': '/EVToken',
        },
        'post_upsert': {
            'command':  'POST',
            'endpoint': '/v2.2/IqPartners/UpdatePartnerRL',
        },
        'post_delete': {
            'command': 'POST',
            'endpoint': '/v2.2/IqPartners/UpdatePartnerRL',
        },
        'get_status': {
            'command': 'GET',
            'endpoint': '/v2.2/IqPartners/GetOperationStatus',
        },
        'get_partner_by_uniqueid': {
            'command':  'GET',
            'endpoint': '/v2.2/IqPartners/GetPartnerByUniqueId',
        },
        'get_risk_by_duns': {
            'command':  'GET',
            'endpoint': '/v2.2/risk',
        },
    }

    DoC = {
        'xls': {
            'evupadm': EviqXlsTaskIoc.evupadm,
            'evupdel': EviqXlsTaskIoc.evupdel,
            'evupreg': EviqXlsTaskIoc.evupreg,
            'evdomap': EviqXlsTaskIoc.evdomap,
        },
        'rst': {
            'evupadm': EviqRstTaskIoc.evupadm,
            'evupdel': EviqRstTaskIoc.evupdel,
            'evupreg': EviqRstTaskIoc.evupreg,
            'evdoexp': EviqRstTaskIoc.evdoexp,
            'evdomap': EviqRstTaskIoc.evdomap,
        },
    }

    sheet_adm = 'Partner verwalten'
    sheet_del = 'Partner entfernen'
    sheet_exp = 'IQ-Export'
    sheet_help = 'Hilfe'

    class InPath:

        evex = 'in_path_evex'
        evup_tmp = 'in_path_evup_tmp'
        evin = 'in_path_evin'

    class OutPath:

        evin_adm_vfy = 'out_path_evin_adm_vfy'
        evin_del_vfy = 'out_path_evin_del_vfy'
        evin_reg_vfy = 'out_path_evin_reg_vfy'

        evup_adm = 'out_path_evup_adm'
        evup_del = 'out_path_evup_del'
        evup_reg = 'out_path_evup_reg'
        evex = 'out_path_evex'

    class Task:

        d_pathnm2datetype = {
            'in_path_evin': 'last',
            'in_path_evex': 'last',
            'in_path_evup_tmp': '',
            'out_path_evin_adm_vfy': 'now',
            'out_path_evin_del_vfy': 'now',
            'out_path_evin_reg_vfy': 'now',
            'out_path_evup_adm': 'now',
            'out_path_evup_del': 'now',
            'out_path_evup_reg': 'now',
            'out_path_evex': 'now',
        }

    class DoSwAdm:

        vfy = True
        vfy_duns = True
        vfy_duns_is_unique = True
        vfy_cpydinm = True
        vfy_regno = True
        vfy_coco = True
        vfy_objectid = True
        vfy_objectid_is_unique = True
        vfy_town = True
        vfy_poco = True
        use_duns = True
        use_evex = True

    class DoSwDel:

        vfy = True
        vfy_objectid = True
        vfy_objectid_is_unique = True
        vfy_iq_id = True
        vfy_iq_id_is_unique = True
        use_evex = True

    class UtilsDe:

        d_ecv_iq2umh_iq = {
            'Sehr niedrig': '1',
            'Niedrig': '2',
            'Mittelniedrig': '3',
            'Mittelhoch': '4',
            'Hoch': '4',
            'Sehr hoch': '4',
            'Undefiniert': '4',
        }
        evin_key_coco = 'Landesvorwahl'
        evin_key_cpydinm = 'Anzeigename des Unternehmens (Ihr Name)'
        evin_key_cpynm = 'Anzeigename des Unternehmens (Ihr Name)'
        evin_key_duns = 'DUNS-Nummer'
        evin_key_iq_id = 'IQ-ID'
        evin_key_objectid = 'Eindeutige ID'
        evin_key_poco = 'Postleitzahl'
        evin_key_regno = 'Steuer-ID oder andere Identifikationsnummer'
        evin_key_town = 'Stadt'

        evex_key_coco = 'Land'

        a_evin_key = [
            'DUNS-Nummer',
            'Steuer-ID',
            'Umsatzsteuer-ID',
            'Handelsregister-Nr',
            'Offizieller Name des Unternehmens',
            'LEI',
        ]
        d_evin2evex_keys = {
            'DUNS-Nummer': 'DUNS-Nummer',
            'Steuer-ID': 'Steuer-ID oder andere Identifikationsnummer',
            'Umsatzsteuer-ID': 'Steuer-ID oder andere Identifikationsnummer',
            'Handelsregister-Nr': 'Steuer-ID oder andere Identifikationsnummer',
            'Offizieller Name des Unternehmens': 'Name des Unternehmens',
            'LEI': 'Steuer-ID oder andere Identifikationsnummer',
            'Eindeutige ID': 'Eindeutige ID',
        }
        d_evex2evin_keys = {
            'Eindeutige ID': 'Eindeutige ID',
            'IQ-ID': 'IQ-ID',
        }
        d_evup_en2de = {
            "UniqueId": "Eindeutige ID",
            "CompanyName": "Offizieller Name des Unternehmens",
            "CriticalityScale": "ScaleAbc",
            "CriticalityLevel": "Kritikalitätsstufe",
            "SpendScale": "ScaleAbc",
            "SpendLevel": "Spend Level",
            "DunsNumber": "DUNS-Nummer",
            "RegistrationNumber": "Steuer-ID oder andere Identifikationsnummer",
            "CountryCode": "Landesvorwahl",
            "Tags": "Tags",
            "contactFirstName": "Vorname des Ansprechpartners beim Unternehmen",
            "contactLastName": "Nachname des Ansprechpartners beim Unternehmen",
            "contactEmail": "Kontakt-Telefonnummer für das Unternehmen",
        },
        d_evup2const = {
            'Anzeigename des Unternehmens (Ihr Name)': None,
            'DUNS-Nummer': '',
            'Steuer-ID oder andere Identifikationsnummer': '',
            'Offizieller Name des Unternehmens': '',

            'Landesvorwahl': '',
            'Postleitzahl': '',
            'Stadt': '',
            'Adresse': '',
            'Eindeutig =ID': '',
            'IQ-ID': '',
            'Kritikalitätsstufe': '',
            'Spend Level': '',

            'Vorname des Ansprechpartners beim Unternehmen': '',
            'Nachname des Ansprechpartners beim Unternehmen': '',
            'E-Mail-Adresse des Ansprechpartners beim Unternehmen': '',
            'Kontakt-Telefonnummer für das Unternehmen': '',
            'E-Mail der anfordernden Kontaktperson': '',

            'Tags': 'Union Investment 2024; KRG',
        }

        doaod_evup2evin_keys = {
            'id1': [
                {
                    'DUNS-Nummer': 'DUNS-Nummer'
                }
            ],
            'id2': [
                {
                    'Steuer-ID oder andere Identifikationsnummer': 'Steuer-ID',
                    'Landesvorwahl': 'Landesvorwahl'
                },
                {
                    'Steuer-ID oder andere Identifikationsnummer':
                        'Umsatzsteuer-ID',
                    'Landesvorwahl': 'Landesvorwahl',
                    'Postleitzahl': 'Postleitzahl',
                    'Stadt': 'Stadt',
                    'Adresse': 'Adresse',
                },
                {
                    'Steuer-ID oder andere Identifikationsnummer':
                        'Handelsregister-Nr',
                    'Landesvorwahl': 'Landesvorwahl',
                    'Postleitzahl': 'Postleitzahl',
                    'Stadt': 'Stadt',
                    'Adresse': 'Adresse',
                },
                {
                    'Steuer-ID oder andere Identifikationsnummer': 'LEI',
                    'Landesvorwahl': 'Landesvorwahl',
                    'Postleitzahl': 'Postleitzahl',
                    'Stadt': 'Stadt',
                    'Adresse': 'Adresse',
                }
            ],
            'id3': [
                {
                    'Offizieller Name des Unternehmens':
                        'Offizieller Name des Unternehmens',
                    'Landesvorwahl': 'Land',
                    'Postleitzahl': 'Postleitzahl',
                    'Stadt': 'Stadt',
                    'Adresse': 'Adresse',
                }
            ]
        }
        d_evup2evin_nonkeys = {
            'Landesvorwahl': 'Landesvorwahl',
            'Postleitzahl': 'Postleitzahl',
            'Stadt': 'Stadt',
            'Adresse': 'Adresse',
            'Eindeutige ID': 'Eindeutige ID',
            'Anzeigename des Unternehmens': 'Anzeigename des Unternehmens',
            'Offizieller Name des Unternehmens': 'Offizieller Name des Unternehmens'
        }
        d_evup2evin_plz_ort_strasse = {
            'Postleitzahl': 'Postleitzahl',
            'Stadt': 'Stadt',
            'Adresse': 'Adresse',
        }
        a_evup_key = [
            'DUNS-Nummer',
            'Steuer-ID oder andere Identifikationsnummer',
            'Offizieller Name des Unternehmens'
        ]
        d_del_evup2evex = {
            'Eindeutige ID': 'Eindeutige ID',
            'IQ-ID': 'IQ-ID',
        }
        d_evup2evex = {
            'IQ-ID': 'IQ-ID',
            'Kritikalitätsstufe': 'Kritikalitätsstufe',
            'Spend Level': 'Spend Level',

            'Vorname des Ansprechpartners beim Unternehmen':
                'Vorname des Ansprechpartners beim Unternehmen',
            'Nachname des Ansprechpartners beim Unternehmen':
                'Nachname des Ansprechpartners beim Unternehmen',
            'E-Mail-Adresse des Ansprechpartners beim Unternehmen':
                'E-Mail-Adresse des Ansprechpartners beim Unternehmen',
            'Kontakt-Telefonnummer für das Unternehmen':
                'Kontakt-Telefonnummer für das Unternehmen',
            'E-Mail der anfordernden Kontaktperson':
                'E-Mail der anfordernden Kontaktperson',
            'Tags': 'Tags'
        }
        d_evup2evin = {
            'Anzeigename des Unternehmens (Ihr Name)':
                'Anzeigename des Unternehmens (Ihr Name)',
            'DUNS-Nummer': 'DUNS-Nummer', 'Offizieller Name des Unternehmens':
                'Offizieller Name des Unternehmens',

            'Landesvorwahl': 'Landesvorwahl',
            'Postleitzahl': 'Postleitzahl',
            'Stadt': 'Stadt',
            'Adresse': 'Adresse',
            'Eindeutige ID': 'Eindeutige ID',
        }
        d_evin2evex = {
            'IQ-ID': 'IQ-ID',
            'Kritikalitätsstufe': 'Kritikalitätsstufe',
            'Spend Level': 'Spend Level',

            'Vorname des Ansprechpartners beim Unternehmen':
                'Vorname des Ansprechpartners beim Unternehmen',
            'Nachname des Ansprechpartners beim Unternehmen':
                'Nachname des Ansprechpartners beim Unternehmen',
            'E-Mail-Adresse des Ansprechpartners beim Unternehmen':
                'E-Mail-Adresse des Ansprechpartners beim Unternehmen',
            'Kontakt-Telefonnummer für das Unternehmen':
                'Kontakt-Telefonnummer für das Unternehmen',
            'E-Mail der anfordernden Kontaktperson':
                'E-Mail der anfordernden Kontaktperson',
            'Tags': 'Tags'
        }
        d_evex2evin = {
            'IQ-ID': 'IQ-ID',
            'Kritikalitätsstufe': 'Kritikalitätsstufe',
            'Spend Level': 'Spend Level',

            'Vorname des Ansprechpartners beim Unternehmen':
                'Vorname des Ansprechpartners beim Unternehmen',
            'Nachname des Ansprechpartners beim Unternehmen':
                'Nachname des Ansprechpartners beim Unternehmen',
            'E-Mail-Adresse des Ansprechpartners beim Unternehmen':
                'E-Mail-Adresse des Ansprechpartners beim Unternehmen',
            'Kontakt-Telefonnummer für das Unternehmen':
                'Kontakt-Telefonnummer für das Unternehmen',
            'E-Mail der anfordernden Kontaktperson':
                'E-Mail der anfordernden Kontaktperson',
            'Tags': 'Tags',
        }
        d_evin2evup = {
            'Offizieller Name des Unternehmens':
                'Offizieller Name des Unternehmens',
            'DUNS-Nummer': 'DUNS-Nummer',
            'Steuer-ID': 'Steuer-ID oder andere Identifikationsnummer',
            'Landesvorwahl': 'Landesvorwahl',
            'Eindeutige ID': 'Eindeutige ID'
        }

    @classmethod
    def set_kwargs(cls, kwargs: TyDic) -> None:
        kwargs['d_pathnm2datetype'] = cls.Task.d_pathnm2datetype
        cls.eviq_lang = kwargs.get('eviq_lang', 'De')
        cls.eviq_if = Dic.loc(cls.DoC, kwargs.get('eviq_if', 'xls'))

        cls._DoC = Dic.loc(cls.DoC, cls.eviq_if)
        if cls.eviq_lang == 'De':
            cls._Utils = cls.UtilsDe
        else:
            cls._Utils = cls.UtilsDe

        cls.DoSwAdm.vfy = kwargs.get('sw_adm_vfy', True)
        cls.DoSwAdm.vfy_duns = kwargs.get('sw_adm_vfy_duns', True)
        cls.DoSwAdm.vfy_duns_is_unique = kwargs.get('sw_adm_vfy_duns_is_unique', True)
        cls.DoSwAdm.vfy_cpydinm = kwargs.get('sw_adm_vfy_cpydinm', True)
        cls.DoSwAdm.vfy_regno = kwargs.get('sw_adm_vfy_regno', True)
        cls.DoSwAdm.vfy_coco = kwargs.get('sw_adm_vfy_coco', True)
        cls.DoSwAdm.vfy_objectid = kwargs.get('sw_adm_vfy_objectid', True)
        cls.DoSwAdm.vfy_objectid_is_unique = kwargs.get(
                'sw_adm_vfy_objectid_is_unique', True)
        cls.DoSwAdm.vfy_town = kwargs.get('sw_adm_vfy_town', False)
        cls.DoSwAdm.vfy_poco = kwargs.get('sw_adm_vfy_poco', True)
        cls.DoSwAdm.use_duns = kwargs.get('sw_adm_vfy_duns', True)

        cls.DoSwDel.vfy = kwargs.get('sw_del_vfy', True)
        cls.DoSwDel.vfy_objectid = kwargs.get('sw_del_vfy_objectid', True)
        cls.DoSwDel.vfy_objectid_is_unique = kwargs.get(
                'sw_del_vfy_objectid_is_unique', True)
        cls.DoSwDel.vfy_iq_id = kwargs.get('sw_del_vfy_iq_id', True)
        cls.DoSwDel.vfy_iq_id_is_unique = kwargs.get('sw_del_vfy_iq_id_is_unique', True)
