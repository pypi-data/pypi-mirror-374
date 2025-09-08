from __future__ import annotations
from typing import List, Dict, Tuple, TypeVar, Type,Any
import hashlib, os
import abc


class BaseMetaClass(abc.ABCMeta):  # pragma: no cover
    def __new__(cls: Type[_T], clsName: str, bases: Tuple[type], attrs: Dict[str, Any]) -> _T:

        

        result = super().__new__(cls, clsName, bases, attrs)

        return result


class BaseObject(object, metaclass=BaseMetaClass):
    pass



_T = TypeVar("_T")
class DeviceInfo(object):
    def __init__(self, model, version) -> None:
        self.model = model
        self.version = version

    def __str__(self) -> str:
        return f"{self.model} {self.version}"


class SystemInfo(BaseObject):

    deviceList: List[DeviceInfo] = []
    device_modesl: List[str] = []
    system_versions: List[str] = []

    def __init__(self) -> None:
        pass

    @classmethod
    def RandomDevice(cls: Type[SystemInfo], unique_id: str = None) -> DeviceInfo:
        hash_id = cls._strtohashid(unique_id)
        return cls._RandomDevice(hash_id)

    @classmethod
    def _RandomDevice(cls, hash_id: int):
        cls.__gen__()
        return cls._hashtovalue(hash_id, cls.deviceList)

    @classmethod
    def __gen__(cls):
        raise NotImplementedError(
            f"{cls.__name__} device not supported for randomize yet"
        )

    @classmethod
    def _strtohashid(cls, unique_id: str = None):

        if unique_id != None and not isinstance(unique_id, str):
            unique_id = str(unique_id)

        byteid = os.urandom(32) if unique_id == None else unique_id.encode("utf-8")

        return int(hashlib.sha1(byteid).hexdigest(), 16) % (10 ** 12)

    @classmethod
    def _hashtorange(cls, hash_id: int, max, min=0):
        return hash_id % (max - min) + min

    @classmethod
    def _hashtovalue(cls, hash_id: int, values: List[_T]) -> _T:
        return values[hash_id % len(values)]

    @classmethod
    def _CleanAndSimplify(cls, text: str) -> str:
        return " ".join(word for word in text.split(" ") if word)


class GeneralDesktopDevice(SystemInfo):

    # Total: 794 devices, update Jan 10th 2022
    # Real device models that I crawled myself from the internet
    #
    # This is the values in HKEY_LOCAL_MACHINE\HARDWARE\DESCRIPTION\System\BIOS
    # including SystemFamily, SystemProductName, BaseBoardProduct
    #
    # Filtered any models that exceed 15 characters
    # just like tdesktop does in lib_base https://github.com/desktop-app/lib_base/blob/master/base/platform/win/base_info_win.cpp#L173
    #
    # Feel free to use
    #
    # Sources: https://answers.microsoft.com/, https://www.techsupportforum.com/ and https://www.bleepingcomputer.com/

    device_models = [
        "0000000000",
        "0133D9",
        "03X0MN",
        "04GJJT",
        "04VWF2",
        "04WT2G",
        "05DN3X",
        "05FFDN",
        "0679",
        "0692FT",
        "06CDVY",
        "07JNH0",
        "0841B1A",
        "0874P6",
        "08VFX1",
        "095TWY",
        "09DKKT",
        "0C1D71",
        "0GDG8Y",
        "0H0CC0",
        "0H869M",
        "0J797R",
        "0JC474",
        "0KM92T",
        "0KP0FT",
        "0KV3RP",
        "0KWVT8",
        "0M277C",
        "0M332H",
        "0M9XW4",
        "0MYG77",
        "0N7TVV",
        "0NWWY0",
        "0P270J",
        "0PD9KD",
        "0PPYW4",
        "0R1203",
        "0R849J",
        "0T105W",
        "0TP406",
        "0U785D",
        "0UU795",
        "0WCNK6",
        "0Y2MRG",
        "0YF8P5",
        "1005P",
        "1005PE",
        "10125",
        "103C_53307F",
        "103C_53307F G=D",
        "103C_53311M HP",
        "103C_53316J",
        "103C_53316J G=D",
        "103C_5335KV",
        "103C_5336AN",
        "1066AWU",
        "110-050eam",
        "122-YW-E173",
        "131-GT-E767",
        "1425",
        "1494",
        "1496",
        "1633",
        "181D",
        "1849",
        "18F9",
        "198C",
        "1998",
        "20060",
        "20216",
        "20245",
        "20250",
        "20266",
        "20351",
        "20384",
        "20ATCTO1WW",
        "20AWA161TH",
        "20BECTO1WW",
        "20HD005EUS",
        "20HES2SF00",
        "20V9",
        "2166",
        "216C",
        "2248",
        "22CD",
        "2349G5P",
        "2378DHU",
        "2A9A",
        "2AB1",
        "2AC8",
        "2AE0",
        "304Bh",
        "3060",
        "30B9",
        "30DC",
        "30F7",
        "3600",
        "3624",
        "3627",
        "3642",
        "3646h",
        "3679CTO",
        "3717",
        "4157RC2",
        "4313CTO",
        "500-056",
        "600-1305t",
        "600-1370",
        "60073",
        "740U5L",
        "765802U",
        "80B8",
        "80C4",
        "80D0",
        "80E3",
        "80E5",
        "80E9",
        "80FC",
        "80RU",
        "80S7",
        "80Y7",
        "8114",
        "81DE",
        "81EF",
        "81H9",
        "81MU",
        "81VV",
        "8216",
        "8217",
        "82KU",
        "838F",
        "843B",
        "844C",
        "84A6",
        "84DA",
        "8582",
        "86F9",
        "8786",
        "8I945PL-G",
        "90NC001MUS",
        "90NC00JBUS",
        "945GT-GN",
        "965P-S3",
        "970A-G/3.1",
        "980DE3/U3S3",
        "990FXA-UD3",
        "A320M-S2H",
        "A320M-S2H-CF",
        "A55M-DGS",
        "A58MD",
        "A78XA-A2T",
        "A7DA 3 series",
        "A88X-PLUS",
        "AB350 Gaming K4",
        "AO533",
        "ASUS MB",
        "AX3400",
        "Acer Desktop",
        "Acer Nitro 5",
        "Alienware",
        "Alienware 17",
        "Alienware 17 R2",
        "Alienware 18",
        "Alienware X51",
        "Alienware m15",
        "All Series",
        "Aspire 4520",
        "Aspire 4736Z",
        "Aspire 5",
        "Aspire 5250",
        "Aspire 5252",
        "Aspire 5536",
        "Aspire 5538G",
        "Aspire 5732Z",
        "Aspire 5735",
        "Aspire 5738",
        "Aspire 5740",
        "Aspire 6930G",
        "Aspire 8950G",
        "Aspire A515-51G",
        "Aspire E5-575G",
        "Aspire M3641",
        "Aspire M5-581T",
        "Aspire M5-581TG",
        "Aspire M5201",
        "Aspire M5802",
        "Aspire M5811",
        "Aspire M7300",
        "Aspire R5-571TG",
        "Aspire T180",
        "Aspire V3-574G",
        "Aspire V5-473G",
        "Aspire V5-552P",
        "Aspire VN7-792G",
        "Aspire X1301",
        "Aspire X1700",
        "Aspire X3400G",
        "Aspire one",
        "Asterope",
        "Aurora",
        "Aurora R5",
        "Aurora-R4",
        "B360M D3H-CF",
        "B360M-D3H",
        "B450M DS3H",
        "B450M DS3H-CF",
        "B550 MB",
        "B550M DS3H",
        "B560 MB",
        "B560M DS3H",
        "B85M-D2V",
        "B85M-G",
        "BDW",
        "Boston",
        "Burbank",
        "C40",
        "CELSIUS R640",
        "CG1330",
        "CG5290",
        "CG8270",
        "CM1630",
        "CathedralPeak",
        "Charmander_KL",
        "CloverTrail",
        "Cuba MS-7301",
        "D102GGC2",
        "D900T",
        "D945GCL",
        "DG41WV",
        "DH61WW",
        "DH67CL",
        "DH77EB",
        "DP55WB",
        "DT1412",
        "DX4300",
        "DX4831",
        "DX4860",
        "DX58SO",
        "Dazzle_RL",
        "Default string",
        "Dell DM061",
        "Dell DV051",
        "Dell DXC061",
        "Dell XPS420",
        "Dell XPS720",
        "Desktop",
        "Dimension 3000",
        "Dimension 4700",
        "Dimension E521",
        "Durian 7A1",
        "EP35-DS3",
        "EP35-DS3R",
        "EP35-DS4",
        "EP35C-DS3R",
        "EP43-DS3L",
        "EP45-DS3L",
        "EP45-UD3L",
        "EP45-UD3LR",
        "EP45-UD3P",
        "EP45-UD3R",
        "EP45T-UD3LR",
        "ET1831",
        "EX58-UD3R",
        "Eee PC",
        "Eureka3",
        "Extensa 5620",
        "Extensa 7620",
        "F2A88X-D3HP",
        "F5SL",
        "F71IX1",
        "FJNB215",
        "FM2A88X Pro3+",
        "FMCP7AM&#160;",
        "Freed_CFS",
        "G1.Assassin2",
        "G31M-ES2L",
        "G31MVP",
        "G31T-M2",
        "G33M-DS2R",
        "G41M-Combo",
        "G41M-ES2L",
        "G41MT-S2P",
        "G53JW",
        "G53SW",
        "G55VW",
        "G60JX",
        "G73Sw",
        "GA-73PVM-S2H",
        "GA-770T-USB3",
        "GA-78LMT-S2P",
        "GA-78LMT-USB3",
        "GA-790FXTA-UD5",
        "GA-870A-UD3",
        "GA-880GM-D2H",
        "GA-880GM-UD2H",
        "GA-880GM-USB3",
        "GA-880GMA-USB3",
        "GA-890GPA-UD3H",
        "GA-890XA-UD3",
        "GA-970A-D3",
        "GA-EA790X-DS4",
        "GA-MA74GM-S2H",
        "GA-MA770-UD3",
        "GA-MA770T-UD3",
        "GA-MA770T-UD3P",
        "GA-MA785GM-US2H",
        "GA-MA785GT-UD3H",
        "GA-MA78G-DS3H",
        "GA-MA78LM-S2H",
        "GA-MA790FX-DQ6",
        "GA-MA790X-DS4",
        "GA-MA790X-UD4",
        "GA401IV",
        "GA502IU",
        "GE60 2OC\\2OE",
        "GF8200E",
        "GL502VMK",
        "GL502VML",
        "GL552VW",
        "GL553VD",
        "GT5636E",
        "GT5654",
        "GT5674",
        "GT70 2OC/2OD",
        "Gateway Desktop",
        "Gateway M280",
        "Godzilla-N10",
        "H110M-A/M.2",
        "H110M-DVS R3.0",
        "H55-USB3",
        "H55M-S2V",
        "H61M-C",
        "H61M-HVS",
        "H61MXL/H61MXL-K",
        "H67M-D2-B3",
        "H81H3-AM",
        "H81M-D PLUS",
        "H87-D3H",
        "H87-D3H-CF",
        "H87-HD3",
        "H97-D3H",
        "H97M Pro4",
        "HP 15",
        "HP 620",
        "HP All-in-One 22-c1xx",
        "HP Compaq 6720s",
        "HP Compaq 8000 Elite SFF",
        "HP Compaq 8100 Elite CMT",
        "HP Compaq 8200 Elite CMT",
        "HP Compaq 8200 Elite USDT",
        "HP Compaq dc7800p Convertible",
        "HP ENVY",
        "HP ENVY 14",
        "HP ENVY 14 Sleekbook",
        "HP ENVY TS m6 Sleekbook",
        "HP ENVY x360 Convertible",
        "HP ENVY x360 m6 Convertible",
        "HP Elite x2 1012 G1",
        "HP EliteBook 6930p",
        "HP EliteBook 8540w",
        "HP EliteDesk 800 G1 SFF",
        "HP G62",
        "HP G70",
        "HP G7000",
        "HP HDX18",
        "HP Laptop 15-da0xxx",
        "HP Pavilion",
        "HP Pavilion 15",
        "HP Pavilion Gaming 690-0xxx",
        "HP Pavilion Gaming 790-0xxx",
        "HP Pavilion P6000 Series",
        "HP Pavilion Sleekbook 14",
        "HP Pavilion dm4",
        "HP Pavilion dv2700",
        "HP Pavilion dv3",
        "HP Pavilion dv4",
        "HP Pavilion dv5",
        "HP Pavilion dv6",
        "HP Pavilion dv7",
        "HP Pavilion g6",
        "HP ProBook 4320s",
        "HP ProBook 450 G2",
        "HP ProBook 4520s",
        "HP ProBook 4530s",
        "HP Spectre x360 Convertible",
        "HPE-498d",
        "HPE-560Z",
        "IDEAPAD",
        "IMEDIA MC 2569",
        "INVALID",
        "ISKAA",
        "IdeaCentre K330",
        "Infoway",
        "Inspiron",
        "Inspiron 1525",
        "Inspiron 1526",
        "Inspiron 1545",
        "Inspiron 1564",
        "Inspiron 1750",
        "Inspiron 3891",
        "Inspiron 518",
        "Inspiron 5570",
        "Inspiron 560",
        "Inspiron 570",
        "Inspiron 6000",
        "Inspiron 620",
        "Inspiron 660",
        "Inspiron 7559",
        "Inspiron 7720",
        "Inspiron N5010",
        "Inspiron N7010",
        "Intel_Mobile",
        "Ironman_SK",
        "K40ID",
        "K43SA",
        "K46CM",
        "K50AB",
        "K52JB",
        "K53SV",
        "K55VD",
        "K56CM",
        "KL3",
        "KM400A-8237",
        "Kabini CRB",
        "LENOVO",
        "LEONITE",
        "LH700",
        "LIFEBOOK SH561",
        "LNVNB161216",
        "LX6810-01",
        "LY325",
        "Lancer 5A2",
        "Lancer 5B2",
        "Latitude",
        "Latitude 3410",
        "Latitude 5400",
        "Latitude 6430U",
        "Latitude 7420",
        "Latitude 7490",
        "Latitude D630",
        "Latitude E4300",
        "Latitude E5450",
        "Latitude E6330",
        "Latitude E6430",
        "Latitude E6510",
        "Latitude E6520",
        "Lenovo B50-70",
        "Lenovo G50-80",
        "Livermore8",
        "M11x R2",
        "M14xR2",
        "M15x",
        "M17x",
        "M2N-E",
        "M2N-SLI",
        "M2N-X",
        "M3A-H/HDMI",
        "M3A770DE",
        "M3N78-AM",
        "M4A785TD-M EVO",
        "M4A785TD-V EVO",
        "M4A78LT-M",
        "M4A78T-E",
        "M4A79 Deluxe",
        "M4A79XTD EVO",
        "M4A87TD/USB3",
        "M4A89GTD-PRO",
        "M4N68T",
        "M4N98TD EVO",
        "M5640/M3640",
        "M570U",
        "M5A78L LE",
        "M5A78L-M LE",
        "M5A78L-M/USB3",
        "M5A87",
        "M5A88-V EVO",
        "M5A97",
        "M5A97 LE R2.0",
        "M5A97 R2.0",
        "M68MT-S2",
        "M750SLI-DS4",
        "M771CUH Lynx",
        "MA51_HX",
        "MAXIMUS V GENE",
        "MCP61PM-AM",
        "MCP73PV",
        "MJ-7592",
        "MS-16GC",
        "MS-1727",
        "MS-17K3",
        "MS-6714",
        "MS-7094",
        "MS-7325",
        "MS-7327",
        "MS-7350",
        "MS-7360",
        "MS-7366",
        "MS-7502",
        "MS-7514",
        "MS-7519",
        "MS-7522",
        "MS-7529",
        "MS-7549",
        "MS-7577",
        "MS-7583",
        "MS-7586",
        "MS-7592",
        "MS-7599",
        "MS-7637",
        "MS-7640",
        "MS-7641",
        "MS-7673",
        "MS-7678",
        "MS-7680",
        "MS-7681",
        "MS-7751",
        "MS-7752",
        "MS-7793",
        "MS-7816",
        "MS-7817",
        "MS-7821",
        "MS-7850",
        "MS-7917",
        "MS-7972",
        "MS-7977",
        "MS-7A34",
        "MS-7A62",
        "MS-7B00",
        "MS-7B46",
        "MS-7C02",
        "MS-7C75",
        "MX8734",
        "Makalu",
        "Mi Laptop",
        "N53SV",
        "N552VX",
        "N55SF",
        "N61Jq",
        "N68-GS3 UCC",
        "N68C-S UCC",
        "N76VZ",
        "N81Vp",
        "NFORCE 680i SLI",
        "NL8K_NL9K",
        "NL9K",
        "NP740U5L-Y03US",
        "NT500R5H-X51M",
        "NUC7i7DNB",
        "NUC7i7DNHE",
        "NV52 Series",
        "NV54 Series",
        "NWQAE",
        "Narra6",
        "Nettle2",
        "Nitro AN515-52",
        "Not Applicable",
        "Notebook PC",
        "OEM",
        "OptiPlex 330",
        "OptiPlex 745",
        "OptiPlex 755",
        "OptiPlex 9010",
        "OptiPlex GX520",
        "P170EM",
        "P170HMx",
        "P35-DS3L",
        "P43-A7",
        "P4M90-M7A",
        "P4P800",
        "P4S-LA",
        "P55-UD4",
        "P55-US3L",
        "P55-USB3",
        "P55A-UD3",
        "P55A-UD3R",
        "P55A-UD4",
        "P55A-UD4P",
        "P55M-UD2",
        "P5E-VM HDMI",
        "P5K PRO",
        "P5N32-E SLI",
        "P5Q SE2",
        "P5Q-PRO",
        "P5QL PRO",
        "P5QL-E",
        "P5QPL-AM",
        "P67A-UD3-B3",
        "P67A-UD4-B3",
        "P67A-UD5-B3",
        "P6T",
        "P6T DELUXE V2",
        "P6T SE",
        "P6X58D PREMIUM",
        "P6X58D-E",
        "P7477A-ABA 751n",
        "P7P55D",
        "P7P55D-E",
        "P7P55D-E LX",
        "P8610",
        "P8H61-M LE/USB3",
        "P8H67-M PRO",
        "P8P67",
        "P8P67 PRO",
        "P8P67-M PRO",
        "P8Z68-V LE",
        "P8Z68-V LX",
        "P8Z68-V PRO",
        "P8Z77-V",
        "P8Z77-V LX",
        "P9X79 LE",
        "PM800-8237",
        "PORTEGE R705",
        "PRIME A320M-K",
        "PRIME B450M-A",
        "PRIME X470-PRO",
        "PRIME Z270-A",
        "PRIME Z390-A",
        "PRIME Z490-V",
        "PWWAA",
        "Polaris_HW",
        "Portable PC",
        "PowerEdge 2950",
        "PowerEdge R515",
        "PowerEdge T420",
        "Precision",
        "Precision 7530",
        "Precision M6500",
        "Proteus IV",
        "QL5",
        "Qosmio X505",
        "R560-LAR39E",
        "ROG",
        "RS690M2MA",
        "RS780HVF",
        "RV415/RV515",
        "S500CA",
        "S550CM",
        "SABERTOOTH P67",
        "SABERTOOTH X58",
        "SAMSUNG ATIV",
        "SG41",
        "SJV50PU",
        "SKL",
        "SM80_HR",
        "SQ9204",
        "STRIKER II NSE",
        "SVE14125CLB",
        "SVE14A25CVW",
        "SX2801",
        "SX2802",
        "Satellite A200",
        "Satellite A215",
        "Satellite A300D",
        "Satellite A500",
        "Satellite A505",
        "Satellite A665",
        "Satellite A665D",
        "Satellite C660",
        "Satellite C855D",
        "Satellite L635",
        "Satellite L650",
        "Satellite P205D",
        "Satellite R630",
        "Shark 2.0",
        "Studio 1458",
        "Studio 1555",
        "Studio 1558",
        "Studio 1747",
        "Studio XPS 1640",
        "Studio XPS 7100",
        "Studio XPS 9100",
        "Suntory_KL",
        "Swift 3",
        "Swift SF314-52",
        "T5212",
        "T5226",
        "T9408UK",
        "TA790GX 128M",
        "TA790GX A3+",
        "TA790GXB3",
        "TA790GXE",
        "TA790GXE 128M",
        "TA990FXE",
        "TM1963",
        "TPower I55",
        "TZ77XE3",
        "ThinkPad L440",
        "ThinkPad T430",
        "ThinkPad T440p",
        "ThinkPad T470",
        "ThinkPad T510",
        "ThinkPad T540p",
        "Type1Family",
        "U50F",
        "UD3R-SLI",
        "UL30VT",
        "USOPP_BH",
        "UX303UB",
        "UX32VD",
        "VAIO",
        "VGN-NR498E",
        "VGN-NW265F",
        "VGN-SR45H_B",
        "VIOLET6",
        "VPCEB27FD",
        "VPCEE31FX",
        "VPCF11QFX",
        "VPCF1290X",
        "VPCF22C5E",
        "VPCF22J1E",
        "VPCS111FM",
        "Veriton E430",
        "VivoBook",
        "Vostro",
        "Vostro 1520",
        "Vostro 1720",
        "Vostro1510",
        "W35xSS_370SS",
        "W55xEU",
        "X421JQ",
        "X510UNR",
        "X550CA",
        "X550JX",
        "X555LAB",
        "X556UB",
        "X556UF",
        "X570 GAMING X",
        "X570 MB",
        "X58-USB3",
        "X58A-UD3R",
        "X58A-UD5",
        "X58A-UD7",
        "XPS",
        "XPS 13 9305",
        "XPS 13 9370",
        "XPS 15 9550",
        "XPS 15 9560",
        "XPS 630i",
        "XPS 730",
        "XPS 730X",
        "XPS 8300",
        "XPS 8700",
        "XPS 8940",
        "XPS A2420",
        "XPS L501X",
        "XPS L701X",
        "XPS M1530",
        "YOGA 530-14ARR",
        "YOGA 920-13IKB",
        "YOGATablet2",
        "Yoga2",
        "Z10PE-D8 WS",
        "Z170 PRO GAMING",
        "Z170-E",
        "Z170X-Gaming 5",
        "Z170X-UD3",
        "Z170X-UD3-CF",
        "Z370P D3",
        "Z370P D3-CF",
        "Z68 Pro3",
        "Z68A-D3-B3",
        "Z68A-D3H-B3",
        "Z68AP-D3",
        "Z68MA-D2H-B3",
        "Z68X-UD3H-B3",
        "Z68XP-UD3",
        "Z68XP-UD4",
        "Z77 Pro4",
        "Z77X-D3H",
        "Z87 Extreme6",
        "Z87-D3HP",
        "Z87-D3HP-CF",
        "Z87M Extreme4",
        "Z87N-WIFI",
        "Z87X-OC",
        "Z87X-OC-CF",
        "Z87X-UD4H",
        "Z97-A",
        "Z97-A-USB31",
        "Z97-AR",
        "Z97-C",
        "Z97-PRO GAMER",
        "Z97X-Gaming 7",
        "eMachines E725",
        "h8-1070t",
        "h8-1534",
        "imedia S3720",
        "ixtreme M5800",
        "p6654y",
        "p6710f",
    ]


class WindowsDevice(GeneralDesktopDevice):
    system_versions = ["Windows 11","Windows 10"]

    deviceList: List[DeviceInfo] = []

    @classmethod
    def __gen__(cls: Type[WindowsDevice]) -> None:

        if len(cls.deviceList) == 0:

            results: List[DeviceInfo] = []

            for model in cls.device_models:
                model = cls._CleanAndSimplify(model.replace("_", ""))
                for version in cls.system_versions:
                    results.append(DeviceInfo(model, version))

            cls.deviceList = results


class LinuxDevice(GeneralDesktopDevice):

    system_versions: List[str] = []
    deviceList: List[DeviceInfo] = []

    @classmethod
    def __gen__(cls: Type[LinuxDevice]) -> None:

        if len(cls.system_versions) == 0:
            # https://github.com/desktop-app/lib_base/blob/master/base/platform/linux/base_info_linux.cpp#L129

            # ? Purposely reduce the amount of devices parameter to generate deviceList more quickly
            enviroments = [
                "GNOME",
                "MATE",
                "XFCE",
                "Cinnamon",
                "Unity",
                "ubuntu",
                "LXDE",
            ]

            wayland = ["Wayland", "XWayland", "X11"]

            libcNames = ["glibc"]
            libcVers = ["2.31", "2.32", "2.33", "2.34"]

            # enviroments = [
            #     "GNOME", "MATE", "XFCE", "Cinnamon", "X-Cinnamon",
            #     "Unity", "ubuntu", "GNOME-Classic", "LXDE"
            # ]

            # wayland = ["Wayland", "XWayland", "X11"]

            # libcNames = ["glibc", "libc"]
            # libcVers = [
            #     "2.20", "2.21", "2.22", "2.23", "2.24", "2.25", "2.26", "2.27",
            #     "2.28", "2.29", "2.30", "2.31", "2.32", "2.33", "2.34"
            # ]

            def getitem(group: List[List[str]], prefix: str = "") -> List[str]:

                prefix = "" if prefix == "" else prefix + " "
                results = []
                if len(group) == 1:
                    for item in group[0]:
                        results.append(prefix + item)
                    return results

                for item in group[0]:
                    results.extend(getitem(group[1:], prefix + item))

                return results

            libcFullNames = getitem([libcNames, libcVers], "")

            cls.system_versions = getitem(
                [enviroments, wayland, libcFullNames], "Linux"
            )

            results: List[DeviceInfo] = []

            for version in cls.system_versions:
                for model in cls.device_models:
                    results.append(DeviceInfo(model, version))

            cls.deviceList = results


class macOSDevice(GeneralDesktopDevice):

    deviceList: List[DeviceInfo] = []

    # Total: 54 device models, update Jan 10th 2022
    # Only list device models since 2013
    #
    # Sources:
    # Thanks to: https://mrmacintosh.com/list-of-mac-boardid-deviceid-model-identifiers-machine-models/
    #       and: https://github.com/brunerd/jamfTools/blob/main/EAs/macOSCompatibility.sh
    #
    # Remark: https://www.innerfence.com/howto/apple-ios-devices-dates-versions-instruction-sets
   
    device_models = [
    "MacBookPro16,4",
    "MacBookPro16,3",
    "MacBookPro16,2",
    "MacBookPro16,1",
    "MacBookPro15,4",
    "MacBookPro15,3",
    "MacBookPro15,2",
    "MacBookPro15,1",
    "MacBookPro14,3",
    "MacBookPro14,2",
    "MacBookPro14,1",
    "MacBookAir9,1",
    "MacBookAir8,2",
    "MacBookAir8,1",
    "MacBook10,1",
    "MacBook9,1",
    "MacPro7,1",
    "iMac20,2",
    "iMac20,1",
    "iMac19,1",
    "iMac18,3",
    "iMac18,2",
    "iMac18,1",
    "iMacPro1,1",
    ]

    # Source: https://support.apple.com/en-us/HT201222
    
    
    system_versions = [
    "macOS 10.14", "macOS 10.14.1", "macOS 10.14.2", "macOS 10.14.3", "macOS 10.14.4", "macOS 10.14.5", "macOS 10.14.6",
    "macOS 10.15", "macOS 10.15.1", "macOS 10.15.2", "macOS 10.15.3", "macOS 10.15.4", "macOS 10.15.5", "macOS 10.15.6", 
    "macOS 10.15.7","macOS 11.0", "macOS 11.0.1", "macOS 11.1", "macOS 11.2", "macOS 11.2.1", "macOS 11.2.2", "macOS 11.2.3", 
    "macOS 11.3", "macOS 11.3.1", "macOS 11.4", "macOS 11.5", "macOS 11.5.1", "macOS 11.5.2", "macOS 11.6", "macOS 11.6.1", 
    "macOS 11.6.2","macOS 12.0", "macOS 12.0.1", "macOS 12.1"]

    deviceList: List[DeviceInfo] = []

    @classmethod
    def __gen__(cls: Type[macOSDevice]) -> None:

        if len(cls.deviceList) == 0:

            # https://github.com/desktop-app/lib_base/blob/master/base/platform/mac/base_info_mac.mm#L42

            def FromIdentifier(model: str):
                words = []
                word = ""

                for ch in model:
                    if not ch.isalpha():
                        continue
                    if ch.isupper():
                        if word != "":
                            words.append(word)
                            word = ""
                    word += ch

                if word != "":
                    words.append(word)
                result = ""
                for word in words:
                    if result != "" and word != "Mac" and word != "Book":
                        result += " "
                    result += word

                return result

            new_devices_models = []
            for model in cls.device_models:
                model = cls._CleanAndSimplify(FromIdentifier(model))
                if not model in new_devices_models:
                    new_devices_models.append(model)

            cls.device_models = new_devices_models

            results: List[DeviceInfo] = []

            for model in cls.device_models:
                for version in cls.system_versions:
                    results.append(DeviceInfo(model, version))

            cls.deviceList = results


class AndroidDevice(SystemInfo):
   
    

    device_models=[
                ("Samsung SM-E066B", "SDK 34"),         # (Android 14) Samsung Galaxy F06 5G Global 
                ("Samsung SM-A066M", "SDK 34"),         # (Android 14) Samsung Galaxy A06 5G LATAM 
                ("Samsung SM-A066E", "SDK 34"),         # (Android 14) Samsung Galaxy A06 5G MEA 
                ("Samsung SM-A066B", "SDK 34"),         # (Android 14) Samsung Galaxy A06 5G Global 
                ("Samsung SM-A065M", "SDK 34"),         # (Android 14) Samsung Galaxy A06 4G LATAM 
                ("Samsung SM-A065F", "SDK 34"),         # (Android 14) Samsung Galaxy A06 4G Global 
                ("Samsung SM-E166P", "SDK 35"),         # (Android 15) Samsung Galaxy F16 5G Global 
                ("Samsung SM-A166U1", "SDK 34"),        # (Android 14) Samsung Galaxy A16 5G US 
                ("Samsung SM-A166U", "SDK 34"),         # (Android 14) Samsung Galaxy A16 5G UW US 
                ("Samsung SM-A166W", "SDK 34"),         # (Android 14) Samsung Galaxy A16 5G CA 
                ("Samsung SM-A1660", "SDK 34"),         # (Android 14) Samsung Galaxy A16 5G CN HK TW 
                ("Samsung SM-A166M", "SDK 34"),         # (Android 14) Samsung Galaxy A16 5G LATAM 
                ("Samsung SM-A166B", "SDK 34"),         # (Android 14) Samsung Galaxy A16 5G EU 
                ("Samsung SM-A166E", "SDK 34"),         # (Android 14) Samsung Galaxy A16 5G MEA 
                ("Samsung SM-A166P", "SDK 34"),         # (Android 14) Samsung Galaxy A16 5G Global 
                ("Samsung SM-A165M", "SDK 34"),         # (Android 14) Samsung Galaxy A16 4G LATAM 
                ("Samsung SM-A165N", "SDK 34"),         # (Android 14) Samsung Galaxy A16 4G KR 
                ("Samsung SM-A165F", "SDK 34"),         # (Android 14) Samsung Galaxy A16 4G EU 
                ("Samsung SM-A566E", "SDK 35"),         # (Android 15) Samsung Galaxy A56 5G Global 
                ("Samsung SM-A5660", "SDK 35"),         # (Android 15) Samsung Galaxy A56 5G CN HK TW 
                ("Samsung SM-A566B", "SDK 35"),         # (Android 15) Samsung Galaxy A56 5G Global 
                ("Samsung SM-A266U1", "SDK 35"),        # (Android 15) Samsung Galaxy A26 5G US 
                ("Samsung SM-A266U", "SDK 35"),         # (Android 15) Samsung Galaxy A26 5G US 
                ("Samsung SM-A266B", "SDK 35"),         # (Android 15) Samsung Galaxy A26 5G Global 
                ("Samsung SM-A266M", "SDK 35"),         # (Android 15) Samsung Galaxy A26 5G LATAM 
                ("Samsung SM-A366U1", "SDK 35"),        # (Android 15) Samsung Galaxy A36 5G US 
                ("Samsung SM-A366U", "SDK 35"),         # (Android 15) Samsung Galaxy A36 5G US 
                ("Samsung SM-A366N", "SDK 35"),         # (Android 15) Samsung Galaxy A36 5G KR 
                ("Samsung SM-A3660", "SDK 35"),         # (Android 15) Samsung Galaxy A36 5G CN HK TW 
                ("Samsung SM-A366W", "SDK 35"),         # (Android 15) Samsung Galaxy A36 5G CA 
                ("Samsung SM-A366E", "SDK 35"),         # (Android 15) Samsung Galaxy A36 5G Global 
                ("Samsung SM-A366B", "SDK 35"),         # (Android 15) Samsung Galaxy A36 5G Global 
                ("Samsung SM-A366D", "SDK 35"),         # (Android 15) Samsung Galaxy A36 5G JP 
                ("Samsung SM-A366Q", "SDK 35"),         # (Android 15) Samsung Galaxy A36 5G JP 
                ("Samsung SM-G990B2", "SDK 34"),        # (Android 14) Samsung Galaxy S21 Fe 5G Global 
                ("Samsung SM-A226BRN", "SDK 33"),       # (Android 13) Samsung Galaxy A22 5G LATAM 
                ("Samsung SM-A226BR", "SDK 33"),        # (Android 13) Samsung Galaxy A22 5G LATAM 
                ("Samsung SM-A253Z", "SDK 35"),         # (Android 15) Samsung Galaxy A25 5G JP 
                ("Samsung SM-A253D", "SDK 35"),         # (Android 15) Samsung Galaxy A25 5G JP 
                ("Samsung SM-A253J", "SDK 35"),         # (Android 15) Samsung Galaxy A25 5G JP 
                ("Samsung SM-A253Q", "SDK 35"),         # (Android 15) Samsung Galaxy A25 5G JP 
                ("Samsung SM-S931Q", "SDK 35"),         # (Android 15) Samsung Galaxy S25 5G JP 
                ("Samsung SM-S931Z", "SDK 35"),         # (Android 15) Samsung Galaxy S25 5G JP 
                ("Samsung SM-S931J", "SDK 35"),         # (Android 15) Samsung Galaxy S25 5G JP 
                ("Samsung SM-S931D", "SDK 35"),         # (Android 15) Samsung Galaxy S25 5G JP 
                ("Samsung SM-S931W", "SDK 35"),         # (Android 15) Samsung Galaxy S25 5G CA 
                ("Samsung SM-S9310", "SDK 35"),         # (Android 15) Samsung Galaxy S25 5G CN HK TW 
                ("Samsung SM-S931N", "SDK 35"),         # (Android 15) Samsung Galaxy S25 5G KR 
                ("Samsung SM-S931U1", "SDK 35"),        # (Android 15) Samsung Galaxy S25 5G UW US 
                ("Samsung SM-S931U", "SDK 35"),         # (Android 15) Samsung Galaxy S25 5G UW US 
                ("Samsung SM-S931B", "SDK 35"),         # (Android 15) Samsung Galaxy S25 5G Global 
                ("Samsung SM-S936W", "SDK 35"),         # (Android 15) Samsung Galaxy S25+ 5G CA 
                ("Samsung SM-S9360", "SDK 35"),         # (Android 15) Samsung Galaxy S25+ 5G CN HK TW 
                ("Samsung SM-S936N", "SDK 35"),         # (Android 15) Samsung Galaxy S25+ 5G UW KR 
                ("Samsung SM-S936U1", "SDK 35"),        # (Android 15) Samsung Galaxy S25+ 5G UW US 
                ("Samsung SM-S936U", "SDK 35"),         # (Android 15) Samsung Galaxy S25+ 5G UW US 
                ("Samsung SM-S936B", "SDK 35"),         # (Android 15) Samsung Galaxy S25+ 5G Global 
                ("Samsung SM-S938W", "SDK 35"),         # (Android 15) Samsung Galaxy S25 Ultra 5G CA 
                ("Samsung SM-S938B", "SDK 35"),         # (Android 15) Samsung Galaxy S25 Ultra 5G Global 
                ("Samsung SM-S9380", "SDK 35"),         # (Android 15) Samsung Galaxy S25 Ultra 5G CN HK TW 
                ("Samsung SM-S938J", "SDK 35"),         # (Android 15) Samsung Galaxy S25 Ultra 5G UW JP 
                ("Samsung SM-S938Z", "SDK 35"),         # (Android 15) Samsung Galaxy S25 Ultra 5G JP 
                ("Samsung SM-S938D", "SDK 35"),         # (Android 15) Samsung Galaxy S25 Ultra 5G UW JP 
                ("Samsung SM-S938Q", "SDK 35"),         # (Android 15) Samsung Galaxy S25 Ultra 5G UW JP 
                ("Samsung SM-S938N", "SDK 35"),         # (Android 15) Samsung Galaxy S25 Ultra 5G UW KR 
                ("Samsung SM-S938U1", "SDK 35"),        # (Android 15) Samsung Galaxy S25 Ultra UW 5G US 
                ("Samsung SM-S938U", "SDK 35"),         # (Android 15) Samsung Galaxy S25 Ultra UW 5G US 
                ("Samsung SM-S721J", "SDK 34"),         # (Android 14) Samsung Galaxy S24 Fe 5G JP 
                ("Samsung SM-S721Q", "SDK 34"),         # (Android 14) Samsung Galaxy S24 Fe 5G JP 
                ("Samsung SM-W7025", "SDK 34"),         # (Android 14) Samsung W25 Flip 5G CN 
                ("Samsung SM-W9025", "SDK 34"),         # (Android 14) Samsung W25 5G CN 
                ("Samsung SM-F958N", "SDK 34"),         # (Android 14) Samsung Galaxy Z Fold 6 5G UW KR 
                ("Samsung SM-S721B", "SDK 34"),         # (Android 14) Samsung Galaxy S24 Fe 5G Global 
                ("Samsung SM-S721N", "SDK 34"),         # (Android 14) Samsung Galaxy S24 Fe 5G KR 
                ("Samsung SM-S721W", "SDK 34"),         # (Android 14) Samsung Galaxy S24 Fe 5G CA 
                ("Samsung SM-S7210", "SDK 34"),         # (Android 14) Samsung Galaxy S24 Fe 5G CN HK TW 
                ("Samsung SM-S721U1", "SDK 34"),        # (Android 14) Samsung Galaxy S24 Fe UW 5G 
                ("Samsung SM-S721U", "SDK 34"),         # (Android 14) Samsung Galaxy S24 Fe UW 5G 
                ("Samsung SM-F741U1", "SDK 34"),        # (Android 14) Samsung Galaxy Z Flip6 5G UW US 
                ("Samsung SM-F741U", "SDK 34"),         # (Android 14) Samsung Galaxy Z Flip6 5G UW US 
                ("Samsung SM-F741W", "SDK 34"),         # (Android 14) Samsung Galaxy Z Flip6 5G CA 
                ("Samsung SM-F741N", "SDK 34"),         # (Android 14) Samsung Galaxy Z Flip6 5G KR 
                ("Samsung SM-F7410", "SDK 34"),         # (Android 14) Samsung Galaxy Z Flip6 5G CN HK TW 
                ("Samsung SM-F741J", "SDK 34"),         # (Android 14) Samsung Galaxy Z Flip6 5G JP 
                ("Samsung SM-F741D", "SDK 34"),         # (Android 14) Samsung Galaxy Z Flip6 5G JP 
                ("Samsung SM-F741Q", "SDK 34"),         # (Android 14) Samsung Galaxy Z Flip6 5G JP 
                ("Samsung SM-F741B", "SDK 34"),         # (Android 14) Samsung Galaxy Z Flip6 5G Global 
                ("Samsung SM-F956U1", "SDK 34"),        # (Android 14) Samsung Galaxy Z Fold6 5G UW US 
                ("Samsung SM-F956U", "SDK 34"),         # (Android 14) Samsung Galaxy Z Fold6 5G UW US 
                ("Samsung SM-F956W", "SDK 34"),         # (Android 14) Samsung Galaxy Z Fold6 5G CA 
                ("Samsung SM-F9560", "SDK 34"),         # (Android 14) Samsung Galaxy Z Fold6 5G CN HK TW 
                ("Samsung SM-F956N", "SDK 34"),         # (Android 14) Samsung Galaxy Z Fold6 5G UW KR 
                ("Samsung SM-F956J", "SDK 34"),         # (Android 14) Samsung Galaxy Z Fold6 5G UW JP 
                ("Samsung SM-F956Q", "SDK 34"),         # (Android 14) Samsung Galaxy Z Fold6 5G UW JP 
                ("Samsung SM-F956D", "SDK 34"),         # (Android 14) Samsung Galaxy Z Fold6 5G UW JP 
                ("Samsung SM-F956B", "SDK 34"),         # (Android 14) Samsung Galaxy Z Fold6 5G Global 
                ("Samsung SM-C5560", "SDK 34"),         # (Android 14) Samsung Galaxy Y55 5G CN 
                ("Samsung SM-E556B", "SDK 34"),         # (Android 14) Samsung Galaxy F55 5G Global 
                ("Samsung SM-S928J", "SDK 34"),         # (Android 14) Samsung Galaxy S24 Ultra 5G UW JP 
                ("Samsung SM-S921J", "SDK 34"),         # (Android 14) Samsung Galaxy S24 5G UW JP 
                ("Samsung SM-M556E", "SDK 34"),         # (Android 14) Samsung Galaxy M55 5G EU 
                ("Samsung SM-M556B", "SDK 34"),         # (Android 14) Samsung Galaxy M55 5G Global 
                ("Samsung SM-G556B", "SDK 34"),         # (Android 14) Samsung Galaxy Xcover7 5G Global 
                ("Samsung SM-S928Q", "SDK 34"),         # (Android 14) Samsung Galaxy S24 Ultra 5G UW JP 
                ("Samsung SM-S921Q", "SDK 34"),         # (Android 14) Samsung Galaxy S24 5G JP 
                ("Samsung SM-A356N", "SDK 34"),         # (Android 14) Samsung Galaxy A35 5G KR 
                ("Samsung SM-A356W", "SDK 34"),         # (Android 14) Samsung Galaxy A35 5G CA 
                ("Samsung SM-A356U", "SDK 34"),         # (Android 14) Samsung Galaxy A35 5G UW US 
                ("Samsung SM-A356U1", "SDK 34"),        # (Android 14) Samsung Galaxy A35 5G UW US 
                ("Samsung SM-A3560", "SDK 34"),         # (Android 14) Samsung Galaxy A35 5G CN HK TW 
                ("Samsung SM-A356B", "SDK 34"),         # (Android 14) Samsung Galaxy A35 5G EU 
                ("Samsung SM-A356E", "SDK 34"),         # (Android 14) Samsung Galaxy A35 5G Global 
                ("Samsung SM-A5560", "SDK 34"),         # (Android 14) Samsung Galaxy A55 5G CN HK TW 
                ("Samsung SM-A556B", "SDK 34"),         # (Android 14) Samsung Galaxy A55 5G EU 
                ("Samsung SM-A556E", "SDK 34"),         # (Android 14) Samsung Galaxy A55 5G Global 
                ("Samsung SM-A556J", "SDK 34"),         # (Android 14) Samsung Galaxy A55 5G JP 
                ("Samsung SM-A556D", "SDK 34"),         # (Android 14) Samsung Galaxy A55 5G JP 
                ("Samsung SM-S921D", "SDK 34"),         # (Android 14) Samsung Galaxy S24 5G UW JP 
                ("Samsung SM-S928D", "SDK 34"),         # (Android 14) Samsung Galaxy S24 Ultra 5G UW JP 
                ("Samsung SM-A137F", "SDK 34"),         # (Android 14) Samsung Galaxy A13 Global 
                ("Samsung SM-M156B", "SDK 34"),         # (Android 14) Samsung Galaxy M15 5G Global 
                ("Samsung SM-F127G", "SDK 33"),         # (Android 13) Samsung Galaxy F12 IN 
                ("Samsung SM-E156B", "SDK 34"),         # (Android 14) Samsung Galaxy F15 5G Global 
                ("Samsung SM-M325FV", "SDK 33"),        # (Android 13) Samsung Galaxy M32 4G Global 
                ("Samsung SM-E346B", "SDK 34"),         # (Android 14) Samsung Galaxy F34 5G IN 
                ("Samsung SM-M346B1", "SDK 34"),        # (Android 14) Samsung Galaxy M34 5G 
                ("Samsung SM-M346B", "SDK 34"),         # (Android 14) Samsung Galaxy M34 5G LATAM IN 
                ("Samsung SM-M346B2", "SDK 34"),        # (Android 14) Samsung Galaxy M34 5G Global 
                ("Samsung SM-A057M", "SDK 34"),         # (Android 14) Samsung Galaxy A05S LATAM 
                ("Samsung SM-A057F", "SDK 34"),         # (Android 14) Samsung Galaxy A05S Global 
                ("Samsung SM-A057G", "SDK 34"),         # (Android 14) Samsung Galaxy A05S EU 
                ("Samsung SM-A055M", "SDK 34"),         # (Android 14) Samsung Galaxy A05 LATAM 
                ("Samsung SM-A055F", "SDK 34"),         # (Android 14) Samsung Galaxy A05 Global 
                ("Samsung SM-A256U", "SDK 34"),         # (Android 14) Samsung Galaxy A25 5G US 
                ("Samsung SM-A256U1", "SDK 34"),        # (Android 14) Samsung Galaxy A25 5G US 
                ("Samsung SM-A256B", "SDK 34"),         # (Android 14) Samsung Galaxy A25 5G EU 
                ("Samsung SM-A2560", "SDK 34"),         # (Android 14) Samsung Galaxy A25 5G CN HK 
                ("Samsung SM-A256N", "SDK 34"),         # (Android 14) Samsung Galaxy A25 5G KR 
                ("Samsung SM-A256EN", "SDK 34"),        # (Android 14) Samsung Galaxy A25 5G 
                ("Samsung SM-A256E", "SDK 34"),         # (Android 14) Samsung Galaxy A25 5G Global 
                ("Samsung SM-A155FN", "SDK 34"),        # (Android 14) Samsung Galaxy A15 4G Global 
                ("Samsung SM-A155F", "SDK 34"),         # (Android 14) Samsung Galaxy A15 4G Global 
                ("Samsung SM-A155MN", "SDK 34"),        # (Android 14) Samsung Galaxy A15 4G LATAM 
                ("Samsung SM-A155M", "SDK 34"),         # (Android 14) Samsung Galaxy A15 4G LATAM 
                ("Samsung SM-A156M", "SDK 34"),         # (Android 14) Samsung Galaxy A15 5G LATAM 
                ("Samsung SM-A156MN", "SDK 34"),        # (Android 14) Samsung Galaxy A15 5G LATAM 
                ("Samsung SM-A156E", "SDK 34"),         # (Android 14) Samsung Galaxy A15 5G Global 
                ("Samsung SM-A156EN", "SDK 34"),        # (Android 14) Samsung Galaxy A15 5G Global 
                ("Samsung SM-A1560", "SDK 34"),         # (Android 14) Samsung Galaxy A15 5G CN HK TW 
                ("Samsung SM-A156B", "SDK 34"),         # (Android 14) Samsung Galaxy A15 5G EU 
                ("Samsung SM-A156U", "SDK 34"),         # (Android 14) Samsung Galaxy A15 5G US 
                ("Samsung SM-A156U1", "SDK 34"),        # (Android 14) Samsung Galaxy A15 5G US 
                ("Samsung SM-A156W", "SDK 34"),         # (Android 14) Samsung Galaxy A15 5G CA 
                ("Samsung SM-S921B", "SDK 34"),         # (Android 14) Samsung Galaxy S24 5G Global 
                ("Samsung SM-S921N", "SDK 34"),         # (Android 14) Samsung Galaxy S24 5G UW KR 
                ("Samsung SM-S921W", "SDK 34"),         # (Android 14) Samsung Galaxy S24 5G CA 
                ("Samsung SM-S9210", "SDK 34"),         # (Android 14) Samsung Galaxy S24 5G CN HK TW 
                ("Samsung SM-S921U", "SDK 34"),         # (Android 14) Samsung Galaxy S24 5G UW US 
                ("Samsung SM-S921U1", "SDK 34"),        # (Android 14) Samsung Galaxy S24 5G UW US 
                ("Samsung SM-S926N", "SDK 34"),         # (Android 14) Samsung Galaxy S24+ 5G UW KR 
                ("Samsung SM-S926B", "SDK 34"),         # (Android 14) Samsung Galaxy S24+ 5G Global 
                ("Samsung SM-S926W", "SDK 34"),         # (Android 14) Samsung Galaxy S24+ 5G CA 
                ("Samsung SM-S9260", "SDK 34"),         # (Android 14) Samsung Galaxy S24+ 5G CN HK TW 
                ("Samsung SM-S926U", "SDK 34"),         # (Android 14) Samsung Galaxy S24+ 5G UW US 
                ("Samsung SM-S926U1", "SDK 34"),        # (Android 14) Samsung Galaxy S24+ 5G UW US 
                ("Samsung SM-S711B", "SDK 34"),         # (Android 14) Samsung Galaxy S23 Fe 5G Global 
                ("Samsung SM-S928B", "SDK 34"),         # (Android 14) Samsung Galaxy S24 Ultra 5G Global 
                ("Samsung SM-S9280", "SDK 34"),         # (Android 14) Samsung Galaxy S24 Ultra 5G CN HK TW 
                ("Samsung SM-S928N", "SDK 34"),         # (Android 14) Samsung Galaxy S24 Ultra 5G UW KR 
                ("Samsung SM-S928W", "SDK 34"),         # (Android 14) Samsung Galaxy S24 Ultra 5G CA 
                ("Samsung SM-S928U1", "SDK 34"),        # (Android 14) Samsung Galaxy S24 Ultra 5G UW US 
                ("Samsung SM-S928U", "SDK 34"),         # (Android 14) Samsung Galaxy S24 Ultra 5G UW US 
                ("Samsung SM-S711W", "SDK 34"),         # (Android 14) Samsung Galaxy S23 Fe 5G CA 
                ("Samsung SM-S711U1", "SDK 34"),        # (Android 14) Samsung Galaxy S23 Fe 5G UW US 
                ("Samsung SM-S711U", "SDK 34"),         # (Android 14) Samsung Galaxy S23 Fe 5G UW US 
                ("Samsung SM-S711J", "SDK 34"),         # (Android 14) Samsung Galaxy S23 Fe 5G 
                ("Samsung SM-S711N", "SDK 34"),         # (Android 14) Samsung Galaxy S23 Fe 5G KR 
                ("Samsung SM-S7110", "SDK 34"),         # (Android 14) Samsung Galaxy S23 Fe 5G CN HK TW 
                ("Samsung SM-W7024", "SDK 34"),         # (Android 14) Samsung W24 Flip 5G CN 
                ("Samsung SM-W9024", "SDK 34"),         # (Android 14) Samsung W24 5G CN 
                ("Samsung SM-F7310", "SDK 34"),         # (Android 14) Samsung Galaxy Z Flip 5 5G CN HK TW 
                ("Samsung SM-F731N", "SDK 34"),         # (Android 14) Samsung Galaxy Z Flip 5 5G KR 
                ("Samsung SM-F9460", "SDK 34"),         # (Android 14) Samsung Galaxy Z Fold5 5G CN HK TW 
                ("Samsung SM-F946B", "SDK 34"),         # (Android 14) Samsung Galaxy Z Fold5 5G Global KR 
                ("Samsung SM-F946N", "SDK 34"),         # (Android 14) Samsung Galaxy Z Fold5 5G UW KR 
                ("Samsung SM-F946U1", "SDK 34"),        # (Android 14) Samsung Galaxy Z Fold5 5G UW US 
                ("Samsung SM-F946U", "SDK 34"),         # (Android 14) Samsung Galaxy Z Fold5 5G UW US 
                ("Samsung SM-F946W", "SDK 34"),         # (Android 14) Samsung Galaxy Z Fold5 5G CA 
                ("Samsung SM-F946Q", "SDK 34"),         # (Android 14) Samsung Galaxy Z Fold5 5G UW JP 
                ("Samsung SM-F946J", "SDK 34"),         # (Android 14) Samsung Galaxy Z Fold5 5G UW JP 
                ("Samsung SM-F946D", "SDK 34"),         # (Android 14) Samsung Galaxy Z Fold5 5G UW JP 
                ("Samsung SM-F731B", "SDK 34"),         # (Android 14) Samsung Galaxy Z Flip 5 5G Global 
                ("Samsung SM-F731W", "SDK 34"),         # (Android 14) Samsung Galaxy Z Flip 5 5G CA 
                ("Samsung SM-F731U1", "SDK 34"),        # (Android 14) Samsung Galaxy Z Flip 5 5G US 
                ("Samsung SM-F731U", "SDK 34"),         # (Android 14) Samsung Galaxy Z Flip 5 5G UW US 
                ("Samsung SM-F731Q", "SDK 34"),         # (Android 14) Samsung Galaxy Z Flip 5 5G UW JP 
                ("Samsung SM-F731J", "SDK 34"),         # (Android 14) Samsung Galaxy Z Flip 5 5G UW JP 
                ("Samsung SM-F731D", "SDK 34"),         # (Android 14) Samsung Galaxy Z Flip 5 5G UW JP 
                ("Samsung SM-A245N", "SDK 34"),         # (Android 14) Samsung Galaxy A24 4G KR 
                ("Samsung SM-A245M", "SDK 34"),         # (Android 14) Samsung Galaxy A24 4G LATAM 
                ("Samsung SM-A245MN", "SDK 34"),        # (Android 14) Samsung Galaxy A24 4G LATAM 
                ("Samsung SM-A245F", "SDK 34"),         # (Android 14) Samsung Galaxy A24 4G Global 
                ("Samsung SM-E146B", "SDK 34"),         # (Android 14) Samsung Galaxy F14 5G Global 
                ("Samsung SM-M146BN", "SDK 34"),        # (Android 14) Samsung Galaxy M14 5G Global 
                ("Samsung SM-M146B", "SDK 34"),         # (Android 14) Samsung Galaxy M14 5G Global 
                ("Samsung SM-M546B", "SDK 34"),         # (Android 14) Samsung Galaxy M54 5G Global 
                ("Samsung SM-A135U", "SDK 34"),         # (Android 14) Samsung Galaxy A13 US 
                ("Samsung SM-A135U1", "SDK 34"),        # (Android 14) Samsung Galaxy A13 US 
                ("Samsung SM-A037F", "SDK 33"),         # (Android 13) Samsung Galaxy A03S Global 
                ("Samsung SM-A127F", "SDK 33"),         # (Android 13) Samsung Galaxy A12 Global 
                ("Samsung SM-S918Q", "SDK 34"),         # (Android 14) Samsung Galaxy S23 Ultra 5G UW JP 
                ("Samsung SM-N976Q", "SDK 33"),         # (Android 13) Samsung Galaxy Note 10+ 5G Global 
                ("Samsung SM-S918N", "SDK 34"),         # (Android 14) Samsung Galaxy S23 Ultra 5G UW KR 
                ("Samsung SM-A145M", "SDK 34"),         # (Android 14) Samsung Galaxy A14 4G LATAM 
                ("Samsung SM-A145P", "SDK 34"),         # (Android 14) Samsung Galaxy A14 4G MEA 
                ("Samsung SM-A145R", "SDK 34"),         # (Android 14) Samsung Galaxy A14 4G EU 
                ("Samsung SM-A145F", "SDK 34"),         # (Android 14) Samsung Galaxy A14 4G Global 
                ("Samsung SM-A2360", "SDK 34"),         # (Android 14) Samsung Galaxy A23 5G CN HK 
                ("Samsung SM-A146M", "SDK 34"),         # (Android 14) Samsung Galaxy A14 5G LATAM 
                ("Samsung SM-A146B", "SDK 34"),         # (Android 14) Samsung Galaxy A14 5G IN 
                ("Samsung SM-A146U", "SDK 34"),         # (Android 14) Samsung Galaxy A14 5G US 
                ("Samsung SM-A047F", "SDK 34"),         # (Android 14) Samsung Galaxy A04S Global 
                ("Samsung SM-A146PN", "SDK 34"),        # (Android 14) Samsung Galaxy A14 5G Global 
                ("Samsung SM-A146P", "SDK 34"),         # (Android 14) Samsung Galaxy A14 5G Global 
                ("Samsung SM-A125W", "SDK 33"),         # (Android 13) Samsung Galaxy A12 CA 
                ("Samsung SM-A536W", "SDK 34"),         # (Android 14) Samsung Galaxy A53 5G CA 
                ("Samsung SM-A037W", "SDK 33"),         # (Android 13) Samsung Galaxy A03S CA 
                ("Samsung SM-A146W", "SDK 34"),         # (Android 14) Samsung Galaxy A14 5G CA 
                ("Samsung SM-A146U1", "SDK 34"),        # (Android 14) Samsung Galaxy A14 5G US 
                ("Samsung SM-A346N", "SDK 34"),         # (Android 14) Samsung Galaxy A34 5G KR 
                ("Samsung SM-A346MN", "SDK 34"),        # (Android 14) Samsung Galaxy A34 5G LATAM 
                ("Samsung SM-A346E", "SDK 34"),         # (Android 14) Samsung Galaxy A34 5G Global 
                ("Samsung SM-A346M", "SDK 34"),         # (Android 14) Samsung Galaxy A34 5G LATAM 
                ("Samsung SM-A346EN", "SDK 34"),        # (Android 14) Samsung Galaxy A34 5G Global 
                ("Samsung SM-A3460", "SDK 34"),         # (Android 14) Samsung Galaxy A34 5G CN HK TW 
                ("Samsung SM-A346B", "SDK 34"),         # (Android 14) Samsung Galaxy A34 5G EU 
                ("Samsung SM-A546U", "SDK 34"),         # (Android 14) Samsung Galaxy A54 5G US 
                ("Samsung SM-A546U1", "SDK 34"),        # (Android 14) Samsung Galaxy A54 5G US 
                ("Samsung SM-A546E", "SDK 34"),         # (Android 14) Samsung Galaxy A54 5G Global 
                ("Samsung SM-A5460", "SDK 34"),         # (Android 14) Samsung Galaxy A54 5G CN HK TW 
                ("Samsung SM-A546J", "SDK 34"),         # (Android 14) Samsung Galaxy A54 5G JP 
                ("Samsung SM-A546D", "SDK 34"),         # (Android 14) Samsung Galaxy A54 5G JP 
                ("Samsung SM-A546B", "SDK 34"),         # (Android 14) Samsung Galaxy A54 5G EU 
                ("Samsung SM-S911U1", "SDK 34"),        # (Android 14) Samsung Galaxy S23 5G UW US 
                ("Samsung SM-S916U1", "SDK 34"),        # (Android 14) Samsung Galaxy S23+ 5G UW US 
                ("Samsung SM-S916U", "SDK 34"),         # (Android 14) Samsung Galaxy S23+ 5G UW US 
                ("Samsung SM-S911U", "SDK 34"),         # (Android 14) Samsung Galaxy S23 5G UW US 
                ("Samsung SM-S918U1", "SDK 34"),        # (Android 14) Samsung Galaxy S23 Ultra 5G UW US 
                ("Samsung SM-S918U", "SDK 34"),         # (Android 14) Samsung Galaxy S23 Ultra 5G UW US 
                ("Samsung SM-S918J", "SDK 34"),         # (Android 14) Samsung Galaxy S23 Ultra 5G UW JP 
                ("Samsung SM-S918D", "SDK 34"),         # (Android 14) Samsung Galaxy S23 Ultra 5G UW JP 
                ("Samsung SM-S918W", "SDK 34"),         # (Android 14) Samsung Galaxy S23 Ultra 5G CA 
                ("Samsung SM-S916W", "SDK 34"),         # (Android 14) Samsung Galaxy S23+ 5G CA 
                ("Samsung SM-S911W", "SDK 34"),         # (Android 14) Samsung Galaxy S23 5G CA 
                ("Samsung SM-S9110", "SDK 34"),         # (Android 14) Samsung Galaxy S23 5G CN 
                ("Samsung SM-S9160", "SDK 34"),         # (Android 14) Samsung Galaxy S23+ 5G CN HK TW 
                ("Samsung SM-S9180", "SDK 34"),         # (Android 14) Samsung Galaxy S23 Ultra 5G CN 
                ("Samsung SM-S916B", "SDK 34"),         # (Android 14) Samsung Galaxy S23+ 5G Global 
                ("Samsung SM-S911B", "SDK 34"),         # (Android 14) Samsung Galaxy S23 5G Global 
                ("Samsung SM-S906E", "SDK 34"),         # (Android 14) Samsung Galaxy S22+ 5G Global 
                ("Samsung SM-S901E", "SDK 34"),         # (Android 14) Samsung Galaxy S22 5G Global 
                ("Samsung SM-S908E", "SDK 34"),         # (Android 14) Samsung Galaxy S22 Ultra 5G Global 
                ("Samsung SM-S911C", "SDK 34"),         # (Android 14) Samsung Galaxy S23 5G UW JP 
                ("Samsung SM-S918B", "SDK 34"),         # (Android 14) Samsung Galaxy S23 Ultra 5G Global 
                ("Samsung SM-S911N", "SDK 34"),         # (Android 14) Samsung Galaxy S23 5G UW KR 
                ("Samsung SM-S916N", "SDK 34"),         # (Android 14) Samsung Galaxy S23+ 5G UW KR 
                ("Samsung SM-S911J", "SDK 34"),         # (Android 14) Samsung Galaxy S23 5G UW JP 
                ("Samsung SM-S911D", "SDK 34"),         # (Android 14) Samsung Galaxy S23 5G UW JP 
                ("Samsung SM-M045F", "SDK 34"),         # (Android 14) Samsung Galaxy M04 Global 
                ("Samsung SM-W7023", "SDK 34"),         # (Android 14) Samsung W23 Flip 5G CN 
                ("Samsung SM-W9023", "SDK 34"),         # (Android 14) Samsung W23 5G CN 
                ("Samsung SM-F721C", "SDK 34"),         # (Android 14) Samsung Galaxy Z Flip 4 5G UW JP 
                ("Samsung SM-M136B", "SDK 34"),         # (Android 14) Samsung Galaxy M13 5G IN 
                ("Samsung SM-E135F", "SDK 34"),         # (Android 14) Samsung Galaxy F13 IN 
                ("Samsung SM-M135M", "SDK 34"),         # (Android 14) Samsung Galaxy M13 LATAM 
                ("Samsung SM-M135FU", "SDK 34"),        # (Android 14) Samsung Galaxy M13 IN 
                ("Samsung SM-M135F", "SDK 34"),         # (Android 14) Samsung Galaxy M13 Global 
                ("Samsung SM-M536B", "SDK 34"),         # (Android 14) Samsung Galaxy M53 5G Global 
                ("Samsung SM-A336N", "SDK 34"),         # (Android 14) Samsung Galaxy A33 5G KR 
                ("Samsung SM-A135N", "SDK 34"),         # (Android 14) Samsung Galaxy A13 KR 
                ("Samsung SM-A235N", "SDK 34"),         # (Android 14) Samsung Galaxy A23 4G KR 
                ("Samsung SM-E045F", "SDK 34"),         # (Android 14) Samsung Galaxy F04 Global 
                ("Samsung SM-A042M", "SDK 34"),         # (Android 14) Samsung Galaxy A04E LATAM 
                ("Samsung SM-A042F", "SDK 34"),         # (Android 14) Samsung Galaxy A04E Global 
                ("Samsung SM-A047M", "SDK 34"),         # (Android 14) Samsung Galaxy A04S LATAM 
                ("Samsung SM-A045M", "SDK 34"),         # (Android 14) Samsung Galaxy A04 LATAM 
                ("Samsung SM-A045F", "SDK 34"),         # (Android 14) Samsung Galaxy A04 Global 
                ("Samsung SM-G736U1", "SDK 34"),        # (Android 14) Samsung Galaxy Xcover6 Pro 5G US 
                ("Samsung SM-G736U", "SDK 34"),         # (Android 14) Samsung Galaxy Xcover6 Pro 5G US 
                ("Samsung SM-G736W", "SDK 34"),         # (Android 14) Samsung Galaxy Xcover6 Pro 5G CA 
                ("Samsung SM-G736B", "SDK 34"),         # (Android 14) Samsung Galaxy Xcover6 Pro 5G Global 
                ("Samsung SM-M336K", "SDK 34"),         # (Android 14) Samsung Galaxy Jump 2 5G Global 
                ("Samsung SM-M536S", "SDK 34"),         # (Android 14) Samsung Galaxy Quantum 3 5G KR 
                ("Samsung SM-M236L", "SDK 34"),         # (Android 14) Samsung Galaxy Buddy 2 5G KR 
                ("Samsung SM-A136S", "SDK 33"),         # (Android 13) Samsung Galaxy Wide6 5G KR 
                ("Samsung SM-A235M", "SDK 34"),         # (Android 14) Samsung Galaxy A23 4G LATAM 
                ("Samsung SM-A235F", "SDK 34"),         # (Android 14) Samsung Galaxy A23 4G Global 
                ("Samsung SM-A235FN", "SDK 34"),        # (Android 14) Samsung Galaxy A23 4G Global 
                ("Samsung SM-A236U", "SDK 34"),         # (Android 14) Samsung Galaxy A23 5G UW US 
                ("Samsung SM-A233C", "SDK 34"),         # (Android 14) Samsung Galaxy A23 5G JP 
                ("Samsung SM-A233J", "SDK 34"),         # (Android 14) Samsung Galaxy A23 5G JP 
                ("Samsung SM-A233D", "SDK 34"),         # (Android 14) Samsung Galaxy A23 5G JP 
                ("Samsung SM-F936J", "SDK 34"),         # (Android 14) Samsung Galaxy Z Fold4 5G UW JP 
                ("Samsung SM-F936D", "SDK 34"),         # (Android 14) Samsung Galaxy Z Fold4 5G UW JP 
                ("Samsung SM-F9360", "SDK 34"),         # (Android 14) Samsung Galaxy Z Fold4 5G CN HK TW 
                ("Samsung SM-F9260", "SDK 33"),         # (Android 13) Samsung Galaxy Z Fold3 5G CN HK TW 
                ("Samsung SM-F936N", "SDK 34"),         # (Android 14) Samsung Galaxy Z Fold4 5G UW KR 
                ("Samsung SM-F936W", "SDK 34"),         # (Android 14) Samsung Galaxy Z Fold4 5G CA 
                ("Samsung SM-F936U1", "SDK 34"),        # (Android 14) Samsung Galaxy Z Fold4 5G UW US 
                ("Samsung SM-F936U", "SDK 34"),         # (Android 14) Samsung Galaxy Z Fold4 5G UW US 
                ("Samsung SM-F936B", "SDK 34"),         # (Android 14) Samsung Galaxy Z Fold4 5G Global 
                ("Samsung SM-F721J", "SDK 34"),         # (Android 14) Samsung Galaxy Z Flip 4 5G UW JP 
                ("Samsung SM-F721D", "SDK 34"),         # (Android 14) Samsung Galaxy Z Flip 4 5G UW JP 
                ("Samsung SM-F7210", "SDK 34"),         # (Android 14) Samsung Galaxy Z Flip 4 5G CN HK TW 
                ("Samsung SM-F721N", "SDK 34"),         # (Android 14) Samsung Galaxy Z Flip 4 5G KR 
                ("Samsung SM-F721B", "SDK 34"),         # (Android 14) Samsung Galaxy Z Flip 4 5G Global 
                ("Samsung SM-F721U1", "SDK 34"),        # (Android 14) Samsung Galaxy Z Flip 4 5G UW 
                ("Samsung SM-F721U", "SDK 34"),         # (Android 14) Samsung Galaxy Z Flip 4 5G UW US 
                ("Samsung SM-F721W", "SDK 34"),         # (Android 14) Samsung Galaxy Z Flip 4 5G CA 
                ("Samsung SM-E236B", "SDK 34"),         # (Android 14) Samsung Galaxy F23 5G IN 
                ("Samsung SM-A236U1", "SDK 34"),        # (Android 14) Samsung Galaxy A23 5G US 
                ("Samsung SM-A236M", "SDK 34"),         # (Android 14) Samsung Galaxy A23 5G LATAM 
                ("Samsung SM-A236E", "SDK 34"),         # (Android 14) Samsung Galaxy A23 5G 
                ("Samsung SM-A236B", "SDK 34"),         # (Android 14) Samsung Galaxy A23 5G Global 
                ("Samsung SM-M236B", "SDK 34"),         # (Android 14) Samsung Galaxy M23 5G Global 
                ("Samsung SM-M236Q", "SDK 34"),         # (Android 14) Samsung Galaxy M23 5G JP 
                ("Samsung SM-A136M", "SDK 33"),         # (Android 13) Samsung Galaxy A13 5G LATAM 
                ("Samsung SM-A136BN", "SDK 33"),        # (Android 13) Samsung Galaxy A13 5G Global 
                ("Samsung SM-A135F", "SDK 34"),         # (Android 14) Samsung Galaxy A13 Global 
                ("Samsung SM-A135M", "SDK 34"),         # (Android 14) Samsung Galaxy A13 LATAM 
                ("Samsung SM-A136B", "SDK 33"),         # (Android 13) Samsung Galaxy A13 5G Global 
                ("Samsung SM-A136U", "SDK 33"),         # (Android 13) Samsung Galaxy A13 5G US 
                ("Samsung SM-G781U1", "SDK 33"),        # (Android 13) Samsung Galaxy S20 Fe 5G UW US 
                ("Samsung SM-G781U", "SDK 33"),         # (Android 13) Samsung Galaxy S20 Fe 5G US 
                ("Samsung SM-G780G", "SDK 33"),         # (Android 13) Samsung Galaxy S20 Fe 
                ("Samsung SM-G781B", "SDK 33"),         # (Android 13) Samsung Galaxy S20 Fe 5G Global 
                ("Samsung SM-J600GT", "SDK 29"),        # (Android 10) Samsung Galaxy J6 Dtv Duos Br 
                ("Samsung SM-G780F", "SDK 33"),         # (Android 13) Samsung Galaxy S20 Fe 
                ("Samsung SM-A305YN", "SDK 31"),        # (Android 12) Samsung Galaxy A30 AU 
                ("Samsung SM-A505GT", "SDK 31"),        # (Android 12) Samsung Galaxy A50 Br 
                ("Samsung SM-A305GT", "SDK 31"),        # (Android 12) Samsung Galaxy A30 Br 
                ("Samsung SM-A035M", "SDK 33"),         # (Android 13) Samsung Galaxy A03 LATAM 
                ("Samsung SM-A035F", "SDK 33"),         # (Android 13) Samsung Galaxy A03 
                ("Samsung SM-A536J", "SDK 34"),         # (Android 14) Samsung Galaxy A53 5G JP 
                ("Samsung SM-A536D", "SDK 34"),         # (Android 14) Samsung Galaxy A53 5G JP 
                ("Samsung SM-A736B", "SDK 34"),         # (Android 14) Samsung Galaxy A73 5G Global 
                ("Samsung SM-M336BU", "SDK 34"),        # (Android 14) Samsung Galaxy M33 5G IN 
                ("Samsung SM-M336B", "SDK 34"),         # (Android 14) Samsung Galaxy M33 5G Global 
                ("Samsung SM-A536U1", "SDK 34"),        # (Android 14) Samsung Galaxy A53 5G US 
                ("Samsung SM-A536U", "SDK 34"),         # (Android 14) Samsung Galaxy A53 5G US 
                ("Samsung SM-A536E", "SDK 34"),         # (Android 14) Samsung Galaxy A53 5G Global 
                ("Samsung SM-A336E", "SDK 34"),         # (Android 14) Samsung Galaxy A33 5G Global 
                ("Samsung SM-A536N", "SDK 34"),         # (Android 14) Samsung Galaxy A53 5G KR 
                ("Samsung SM-A3360", "SDK 34"),         # (Android 14) Samsung Galaxy A33 5G CN HK 
                ("Samsung SM-A5360", "SDK 34"),         # (Android 14) Samsung Galaxy A53 5G CN HK TW 
                ("Samsung SM-A536B", "SDK 34"),         # (Android 14) Samsung Galaxy A53 5G EU 
                ("Samsung SM-A336B", "SDK 34"),         # (Android 14) Samsung Galaxy A33 5G EU LATAM 
                ("Samsung SM-W2022", "SDK 33"),         # (Android 13) Samsung W22 5G CN 
                ("Samsung SM-S908B", "SDK 34"),         # (Android 14) Samsung Galaxy S22 Ultra 5G EU 
                ("Samsung SM-S906W", "SDK 34"),         # (Android 14) Samsung Galaxy S22+ 5G CA 
                ("Samsung SM-S901W", "SDK 34"),         # (Android 14) Samsung Galaxy S22 5G CA 
                ("Samsung SM-S908W", "SDK 34"),         # (Android 14) Samsung Galaxy S22 Ultra 5G CA 
                ("Samsung SM-S9010", "SDK 34"),         # (Android 14) Samsung Galaxy S22 5G CN HK TW 
                ("Samsung SM-S9060", "SDK 34"),         # (Android 14) Samsung Galaxy S22+ 5G UW CN HK TW 
                ("Samsung SM-S9080", "SDK 34"),         # (Android 14) Samsung Galaxy S22 Ultra 5G UW CN HK TW 
                ("Samsung SM-S901N", "SDK 34"),         # (Android 14) Samsung Galaxy S22 5G KR 
                ("Samsung SM-S906N", "SDK 34"),         # (Android 14) Samsung Galaxy S22+ 5G UW KR 
                ("Samsung SM-S908N", "SDK 34"),         # (Android 14) Samsung Galaxy S22 Ultra 5G UW KR 
                ("Samsung SM-S906U1", "SDK 34"),        # (Android 14) Samsung Galaxy S22+ 5G UW US 
                ("Samsung SM-S906U", "SDK 34"),         # (Android 14) Samsung Galaxy S22+ 5G UW US 
                ("Samsung SM-S908U1", "SDK 34"),        # (Android 14) Samsung Galaxy S22 Ultra 5G UW US 
                ("Samsung SM-S908U", "SDK 34"),         # (Android 14) Samsung Galaxy S22 Ultra 5G UW US 
                ("Samsung SM-S901U1", "SDK 34"),        # (Android 14) Samsung Galaxy S22 5G UW US 
                ("Samsung SM-S901U", "SDK 34"),         # (Android 14) Samsung Galaxy S22 5G UW US 
                ("Samsung SM-S901J", "SDK 34"),         # (Android 14) Samsung Galaxy S22 5G UW JP 
                ("Samsung SM-S901D", "SDK 34"),         # (Android 14) Samsung Galaxy S22 5G UW JP 
                ("Samsung SM-S908J", "SDK 34"),         # (Android 14) Samsung Galaxy S22 Ultra 5G UW JP 
                ("Samsung SM-S908D", "SDK 34"),         # (Android 14) Samsung Galaxy S22 Ultra 5G UW JP 
                ("Samsung SM-S906B", "SDK 34"),         # (Android 14) Samsung Galaxy S22+ 5G EU 
                ("Samsung SM-S901B", "SDK 34"),         # (Android 14) Samsung Galaxy S22 5G EU 
                ("Samsung SM-M225FV", "SDK 33"),        # (Android 13) Samsung Galaxy M22 4G Global 
                ("Samsung SM-A223D", "SDK 33"),         # (Android 13) Samsung Galaxy A22 5G JP 
                ("Samsung SM-M526BR", "SDK 33"),        # (Android 13) Samsung Galaxy M52 5G Global 
                ("Samsung SM-M526B", "SDK 33"),         # (Android 13) Samsung Galaxy M52 5G Global 
                ("Samsung SM-E426B", "SDK 33"),         # (Android 13) Samsung Galaxy F42 5G Global 
                ("Samsung SM-G990N", "SDK 34"),         # (Android 14) Samsung Galaxy S21 Fe 5G UW KR 
                ("Samsung SM-G990W", "SDK 34"),         # (Android 14) Samsung Galaxy S21 Fe 5G CA 
                ("Samsung SM-G990U1", "SDK 34"),        # (Android 14) Samsung Galaxy S21 Fe 5G UW US 
                ("Samsung SM-G990U", "SDK 34"),         # (Android 14) Samsung Galaxy S21 Fe 5G UW US 
                ("Samsung SM-G990E", "SDK 34"),         # (Android 14) Samsung Galaxy S21 Fe 5G MEA 
                ("Samsung SM-G9900", "SDK 34"),         # (Android 14) Samsung Galaxy S21 Fe 5G CN TW HK 
                ("Samsung SM-G990B", "SDK 34"),         # (Android 14) Samsung Galaxy S21 Fe 5G Global 
                ("Samsung SM-G715FN", "SDK 33"),        # (Android 13) Samsung Galaxy Xcover Pro Global 
                ("Samsung SM-G525F", "SDK 33"),         # (Android 13) Samsung Galaxy Xcover 5 Global 
                ("Samsung SM-F926B", "SDK 33"),         # (Android 13) Samsung Galaxy Z Fold3 5G Global 
                ("Samsung SM-F926U1", "SDK 33"),        # (Android 13) Samsung Galaxy Z Fold3 5G UW US 
                ("Samsung SM-F926W", "SDK 33"),         # (Android 13) Samsung Galaxy Z Fold3 5G CA 
                ("Samsung SM-F926U", "SDK 33"),         # (Android 13) Samsung Galaxy Z Fold3 5G UW US 
                ("Samsung SM-F926N", "SDK 33"),         # (Android 13) Samsung Galaxy Z Fold3 5G UW KR 
                ("Samsung SM-A528N", "SDK 33"),         # (Android 13) Samsung Galaxy A52S 5G KR 
                ("Samsung SM-G525N", "SDK 33"),         # (Android 13) Samsung Galaxy Xcover 5 KR 
                ("Samsung SM-A226L", "SDK 33"),         # (Android 13) Samsung Galaxy Buddy 5G KR 
                ("Samsung SM-E426S", "SDK 33"),         # (Android 13) Samsung Galaxy Wide5 5G KR 
                ("Samsung SM-F926D", "SDK 33"),         # (Android 13) Samsung Galaxy Z Fold3 5G UW JP 
                ("Samsung SM-F926J", "SDK 33"),         # (Android 13) Samsung Galaxy Z Fold3 5G UW JP 
                ("Samsung SM-F711B", "SDK 33"),         # (Android 13) Samsung Galaxy Z Flip 3 5G Global 
                ("Samsung SM-F711J", "SDK 33"),         # (Android 13) Samsung Galaxy Z Flip 3 5G JP 
                ("Samsung SM-F711D", "SDK 33"),         # (Android 13) Samsung Galaxy Z Flip 3 5G JP 
                ("Samsung SM-F7110", "SDK 33"),         # (Android 13) Samsung Galaxy Z Flip 3 5G CN HK TW 
                ("Samsung SM-F711N", "SDK 33"),         # (Android 13) Samsung Galaxy Z Flip 3 5G KR 
                ("Samsung SM-F711W", "SDK 33"),         # (Android 13) Samsung Galaxy Z Flip 3 5G CA 
                ("Samsung SM-F711U1", "SDK 33"),        # (Android 13) Samsung Galaxy Z Flip 3 5G UW US 
                ("Samsung SM-F711U", "SDK 33"),         # (Android 13) Samsung Galaxy Z Flip 3 5G UW US 
                ("Samsung SM-A037U", "SDK 33"),         # (Android 13) Samsung Galaxy A03S US 
                ("Samsung SM-A136U1", "SDK 33"),        # (Android 13) Samsung Galaxy A13 5G US 
                ("Samsung SM-A136W", "SDK 33"),         # (Android 13) Samsung Galaxy A13 5G CA 
                ("Samsung SM-A035G", "SDK 33"),         # (Android 13) Samsung Galaxy A03 Global 
                ("Samsung SM-A037G", "SDK 33"),         # (Android 13) Samsung Galaxy A03S Global 
                ("Samsung SM-A037M", "SDK 33"),         # (Android 13) Samsung Galaxy A03S LATAM 
                ("Samsung SM-E225F", "SDK 33"),         # (Android 13) Samsung Galaxy F22 4G IN 
                ("Samsung SM-A528B", "SDK 33"),         # (Android 13) Samsung Galaxy A52S 5G Global 
                ("Samsung SM-A127M", "SDK 33"),         # (Android 13) Samsung Galaxy A12 Nacho LATAM 
                ("Samsung SM-A025U", "SDK 33"),         # (Android 13) Samsung Galaxy A02S US 
                ("Samsung SM-A526U", "SDK 33"),         # (Android 13) Samsung Galaxy A52 5G US 
                ("Samsung SM-A326U1", "SDK 33"),        # (Android 13) Samsung Galaxy A32 5G US 
                ("Samsung SM-A426U", "SDK 33"),         # (Android 13) Samsung Galaxy A42 5G UW US 
                ("Samsung SM-A426U1", "SDK 33"),        # (Android 13) Samsung Galaxy A42 5G UW US 
                ("Samsung SM-A125U", "SDK 33"),         # (Android 13) Samsung Galaxy A12 US 
                ("Samsung SM-A600T", "SDK 29"),         # (Android 10) Samsung Galaxy A6 US 
                ("Samsung SM-A600U", "SDK 29"),         # (Android 10) Samsung Galaxy A6 US 
                ("Samsung SM-A600P", "SDK 29"),         # (Android 10) Samsung Galaxy A6 US 
                ("Samsung SM-A600A", "SDK 29"),         # (Android 10) Samsung Galaxy A6 US 
                ("Samsung SM-A505U", "SDK 31"),         # (Android 12) Samsung Galaxy A50 US 
                ("Samsung SM-A115U", "SDK 33"),         # (Android 13) Samsung Galaxy A11 US 
                ("Samsung SM-A115U1", "SDK 33"),        # (Android 13) Samsung Galaxy A11 US 
                ("Samsung SM-A215U", "SDK 33"),         # (Android 13) Samsung Galaxy A21 US 
                ("Samsung SM-A102U", "SDK 31"),         # (Android 12) Samsung Galaxy A10E US 
                ("Samsung SM-A205U1", "SDK 31"),        # (Android 12) Samsung Galaxy A20 US 
                ("Samsung SM-A205U", "SDK 31"),         # (Android 12) Samsung Galaxy A20 US 
                ("Samsung SM-A716U", "SDK 33"),         # (Android 13) Samsung Galaxy A71 5G US 
                ("Samsung SM-A716U1", "SDK 33"),        # (Android 13) Samsung Galaxy A71 5G US 
                ("Samsung SM-A516U", "SDK 33"),         # (Android 13) Samsung Galaxy A51 5G US 
                ("Samsung SM-M215G", "SDK 33"),         # (Android 13) Samsung Galaxy M21 Global 
                ("Samsung SM-A326U", "SDK 33"),         # (Android 13) Samsung Galaxy A32 5G US 
                ("Samsung SM-A025V", "SDK 33"),         # (Android 13) Samsung Galaxy A02S US 
                ("Samsung SM-A025U1", "SDK 33"),        # (Android 13) Samsung Galaxy A02S US 
                ("Samsung SM-A125U1", "SDK 33"),        # (Android 13) Samsung Galaxy A12 US 
                ("Samsung SM-A826S", "SDK 33"),         # (Android 13) Samsung Galaxy Quantum 2 5G KR 
                ("Samsung SM-M127N", "SDK 33"),         # (Android 13) Samsung Galaxy M12 KR 
                ("Samsung SM-A315N", "SDK 33"),         # (Android 13) Samsung Galaxy A31 KR 
                ("Samsung SM-A217N", "SDK 33"),         # (Android 13) Samsung Galaxy A21S KR 
                ("Samsung SM-A325N", "SDK 33"),         # (Android 13) Samsung Galaxy A32 4G KR 
                ("Samsung SM-A426N", "SDK 33"),         # (Android 13) Samsung Galaxy A42 5G KR 
                ("Samsung SM-G781N", "SDK 33"),         # (Android 13) Samsung Galaxy S20 Fe 5G KR 
                ("Samsung SM-G991N", "SDK 33"),         # (Android 13) Samsung Galaxy S21 5G KR 
                ("Samsung SM-G996N", "SDK 33"),         # (Android 13) Samsung Galaxy S21+ 5G UW KR 
                ("Samsung SM-G998N", "SDK 33"),         # (Android 13) Samsung Galaxy S21 Ultra 5G UW KR 
                ("Samsung SM-E5260", "SDK 33"),         # (Android 13) Samsung Galaxy F52 5G CN 
                ("Samsung SM-F7000", "SDK 33"),         # (Android 13) Samsung Galaxy Z Flip CN 
                ("Samsung SM-A426B", "SDK 33"),         # (Android 13) Samsung Galaxy A42 5G Global 
                ("Samsung SM-A217F", "SDK 33"),         # (Android 13) Samsung Galaxy A21S Global 
                ("Samsung SM-A125F", "SDK 33"),         # (Android 13) Samsung Galaxy A12 Global 
                ("Samsung SM-A525F", "SDK 33"),         # (Android 13) Samsung Galaxy A52 Global 
                ("Samsung SM-A725F", "SDK 33"),         # (Android 13) Samsung Galaxy A72 Global 
                ("Samsung SM-M317F", "SDK 33"),         # (Android 13) Samsung Galaxy M31S Global 
                ("Samsung SM-M127F", "SDK 33"),         # (Android 13) Samsung Galaxy M12 Global 
                ("Samsung SM-A516B", "SDK 33"),         # (Android 13) Samsung Galaxy A51 5G Global 
                ("Samsung SM-A326B", "SDK 33"),         # (Android 13) Samsung Galaxy A32 5G Global 
                ("Samsung SM-J600G", "SDK 29"),         # (Android 10) Samsung Galaxy J6 LATAM 
                ("Samsung SM-A605GN", "SDK 29"),        # (Android 10) Samsung Galaxy A6+ LATAM 
                ("Samsung SM-A750G", "SDK 29"),         # (Android 10) Samsung Galaxy A7 LATAM 
                ("Samsung SM-A750GN", "SDK 29"),        # (Android 10) Samsung Galaxy A7 Duos 
                ("Samsung SM-A305G", "SDK 31"),         # (Android 12) Samsung Galaxy A30 LATAM 
                ("Samsung SM-A505G", "SDK 31"),         # (Android 12) Samsung Galaxy A50 LATAM 
                ("Samsung SM-A205G", "SDK 31"),         # (Android 12) Samsung Galaxy A20 LATAM 
                ("Samsung SM-A207M", "SDK 31"),         # (Android 12) Samsung Galaxy A20S LATAM 
                ("Samsung SM-A307G", "SDK 31"),         # (Android 12) Samsung Galaxy A30S LATAM 
                ("Samsung SM-A515F", "SDK 33"),         # (Android 13) Samsung Galaxy A51 Global 
                ("Samsung SM-A715F", "SDK 33"),         # (Android 13) Samsung Galaxy A71 Global 
                ("Samsung SM-A115M", "SDK 33"),         # (Android 13) Samsung Galaxy A11 LATAM 
                ("Samsung SM-A315G", "SDK 33"),         # (Android 13) Samsung Galaxy A31 Global 
                ("Samsung SM-A315GL", "SDK 33"),        # (Android 13) Samsung Galaxy A31 LATAM 
                ("Samsung SM-A125M", "SDK 33"),         # (Android 13) Samsung Galaxy A12 LATAM 
                ("Samsung SM-J810M", "SDK 29"),         # (Android 10) Samsung Galaxy J8 Duos LATAM 
                ("Samsung SM-M022M", "SDK 33"),         # (Android 13) Samsung Galaxy M02 LATAM 
                ("Samsung SM-A105M", "SDK 31"),         # (Android 12) Samsung Galaxy A10 LATAM 
                ("Samsung SM-A217M", "SDK 33"),         # (Android 13) Samsung Galaxy A21S LATAM 
                ("Samsung SM-A525M", "SDK 33"),         # (Android 13) Samsung Galaxy A52 LATAM 
                ("Samsung SM-A325M", "SDK 33"),         # (Android 13) Samsung Galaxy A32 4G LATAM 
                ("Samsung SM-A022M", "SDK 33"),         # (Android 13) Samsung Galaxy A02 LATAM 
                ("Samsung SM-A025M", "SDK 33"),         # (Android 13) Samsung Galaxy A02S LATAM 
                ("Samsung SM-A225MN", "SDK 33"),        # (Android 13) Samsung Galaxy A22 4G LATAM 
                ("Samsung SM-A225M", "SDK 33"),         # (Android 13) Samsung Galaxy A22 4G LATAM 
                ("Samsung SM-A225F", "SDK 33"),         # (Android 13) Samsung Galaxy A22 4G Global 
                ("Samsung SM-A226B", "SDK 33"),         # (Android 13) Samsung Galaxy A22 5G Global 
                ("Samsung SM-E025F", "SDK 33"),         # (Android 13) Samsung Galaxy F02S Global 
                ("Samsung SM-M325F", "SDK 33"),         # (Android 13) Samsung Galaxy M32 4G Global 
                ("Samsung SM-A325F", "SDK 33"),         # (Android 13) Samsung Galaxy A32 4G Global 
                ("Samsung SM-A725M", "SDK 33"),         # (Android 13) Samsung Galaxy A72 LATAM 
                ("Samsung SM-M115M", "SDK 33"),         # (Android 13) Samsung Galaxy M11 LATAM 
                ("Samsung SM-A705GM", "SDK 31"),        # (Android 12) Samsung Galaxy A70 IN 
                ("Samsung SM-A705FN", "SDK 31"),        # (Android 12) Samsung Galaxy A70 Global 
                ("Samsung SM-A315F", "SDK 33"),         # (Android 13) Samsung Galaxy A31 IN 
                ("Samsung SM-A205S", "SDK 31"),         # (Android 12) Samsung Galaxy Wide 4 KR 
                ("Samsung SM-J737S", "SDK 29"),         # (Android 10) Samsung Galaxy Wide 3 KR 
                ("Samsung SM-A202K", "SDK 31"),         # (Android 12) Samsung Galaxy Jean 2 KR 
                ("Samsung SM-G9960", "SDK 33"),         # (Android 13) Samsung Galaxy S21+ 5G CN HK 
                ("Samsung SM-G9910", "SDK 33"),         # (Android 13) Samsung Galaxy S21 5G CN HK 
                ("Samsung SM-G9980", "SDK 33"),         # (Android 13) Samsung Galaxy S21 Ultra 5G CN HK 
                ("Samsung SM-F916W", "SDK 33"),         # (Android 13) Samsung Galaxy Z Fold2 5G CA 
                ("Samsung SM-F700W", "SDK 33"),         # (Android 13) Samsung Galaxy Z Flip CA 
                ("Samsung SM-F707W", "SDK 33"),         # (Android 13) Samsung Galaxy Z Flip 5G CA 
                ("Samsung SM-A115W", "SDK 33"),         # (Android 13) Samsung Galaxy A11 CA 
                ("Samsung SM-A515W", "SDK 33"),         # (Android 13) Samsung Galaxy A51 CA 
                ("Samsung SM-A715W", "SDK 33"),         # (Android 13) Samsung Galaxy A71 CA 
                ("Samsung SM-A326W", "SDK 33"),         # (Android 13) Samsung Galaxy A32 5G CA 
                ("Samsung SM-G991J", "SDK 33"),         # (Android 13) Samsung Galaxy S21 5G UW JP 
                ("Samsung SM-G996J", "SDK 33"),         # (Android 13) Samsung Galaxy S21+ 5G JP 
                ("Samsung SM-G991D", "SDK 33"),         # (Android 13) Samsung Galaxy S21 5G UW JP 
                ("Samsung SM-A526D", "SDK 33"),         # (Android 13) Samsung Galaxy A52 5G JP 
                ("Samsung SM-G998D", "SDK 33"),         # (Android 13) Samsung Galaxy S21 Ultra 5G UW JP 
                ("Samsung SM-G998W", "SDK 33"),         # (Android 13) Samsung Galaxy S21 Ultra 5G CA 
                ("Samsung SM-G996B", "SDK 33"),         # (Android 13) Samsung Galaxy S21+ 5G Global 
                ("Samsung SM-G998B", "SDK 33"),         # (Android 13) Samsung Galaxy S21 Ultra 5G Global 
                ("Samsung SM-G988B", "SDK 33"),         # (Android 13) Samsung Galaxy S20 Ultra 5G Global 
                ("Samsung SM-G998U", "SDK 33"),         # (Android 13) Samsung Galaxy S21 Ultra 5G UW US 
                ("Samsung SM-G998U1", "SDK 33"),        # (Android 13) Samsung Galaxy S21 Ultra 5G UW US 
                ("Samsung SM-G991U", "SDK 33"),         # (Android 13) Samsung Galaxy S21 5G UW US 
                ("Samsung SM-G996U", "SDK 33"),         # (Android 13) Samsung Galaxy S21+ 5G UW US 
                ("Samsung SM-G996U1", "SDK 33"),        # (Android 13) Samsung Galaxy S21+ 5G UW US 
                ("Samsung SM-G991U1", "SDK 33"),        # (Android 13) Samsung Galaxy S21 5G UW US 
                ("Samsung SM-G996W", "SDK 33"),         # (Android 13) Samsung Galaxy S21+ 5G CA 
                ("Samsung SM-G991W", "SDK 33"),         # (Android 13) Samsung Galaxy S21 5G CA 
                ("Samsung SM-G991B", "SDK 33"),         # (Android 13) Samsung Galaxy S21 5G Global 
                ("Samsung SM-M022G", "SDK 33"),         # (Android 13) Samsung Galaxy M02 IN 
                ("Samsung SM-A526N", "SDK 33"),         # (Android 13) Samsung Galaxy A52 5G KR 
                ("Samsung SM-A125N", "SDK 33"),         # (Android 13) Samsung Galaxy A12 KR 
                ("Samsung SM-A526W", "SDK 33"),         # (Android 13) Samsung Galaxy A52 5G CA 
                ("Samsung SM-A326K", "SDK 33"),         # (Android 13) Samsung Galaxy Jump 5G KR 
                ("Samsung SM-A526U1", "SDK 33"),        # (Android 13) Samsung Galaxy A52 5G US 
                ("Samsung SM-A5260", "SDK 33"),         # (Android 13) Samsung Galaxy A52 5G CN TW 
                ("Samsung SM-A526B", "SDK 33"),         # (Android 13) Samsung Galaxy A52 5G Global 
                ("Samsung SM-M127G", "SDK 33"),         # (Android 13) Samsung Galaxy M12 IN 
                ("Samsung SM-M625F", "SDK 33"),         # (Android 13) Samsung Galaxy M62 Global 
                ("Samsung SM-A022F", "SDK 33"),         # (Android 13) Samsung Galaxy A02 Global 
                ("Samsung SM-A326J", "SDK 33"),         # (Android 13) Samsung Galaxy A32 5G JP 
                ("Samsung SM-E625F", "SDK 33"),         # (Android 13) Samsung Galaxy F62 Global 
                ("Samsung SM-A025F", "SDK 33"),         # (Android 13) Samsung Galaxy A02S Global 
                ("Samsung SM-A022G", "SDK 33"),         # (Android 13) Samsung Galaxy A02 
                ("Samsung SM-A025G", "SDK 33"),         # (Android 13) Samsung Galaxy A02S Global 
                ("Samsung SM-M025F", "SDK 33"),         # (Android 13) Samsung Galaxy M02S Global 
                ("Samsung SM-M315F", "SDK 33"),         # (Android 13) Samsung Galaxy M31 Prime Global 
                ("Samsung SM-G715W", "SDK 33"),         # (Android 13) Samsung Galaxy Xcover Pro CA 
                ("Samsung SM-G715U", "SDK 33"),         # (Android 13) Samsung Galaxy Xcover Pro US 
                ("Samsung SM-G715U1", "SDK 33"),        # (Android 13) Samsung Galaxy Xcover Pro US 
                ("Samsung SM-W2021", "SDK 33"),         # (Android 13) Samsung W21 5G CN 
                ("Samsung SM-A102J", "SDK 33"),         # (Android 13) Samsung Galaxy A21 Simple JP 
                ("Samsung SM-A102D", "SDK 33"),         # (Android 13) Samsung Galaxy A21 JP 
                ("Samsung SM-F415F", "SDK 33"),         # (Android 13) Samsung Galaxy F41 Global 
                ("Samsung SM-M515F", "SDK 33"),         # (Android 13) Samsung Galaxy M51 Global 
                ("Samsung SM-F916U1", "SDK 33"),        # (Android 13) Samsung Galaxy Z Fold2 UW 5G US 
                ("Samsung SM-F916B", "SDK 33"),         # (Android 13) Samsung Galaxy Z Fold2 5G Global 
                ("Samsung SM-F9160", "SDK 33"),         # (Android 13) Samsung Galaxy Z Fold2 5G CN HK 
                ("Samsung SM-G7810", "SDK 33"),         # (Android 13) Samsung Galaxy S20 Fe 5G CN 
                ("Samsung SM-F916U", "SDK 33"),         # (Android 13) Samsung Galaxy Z Fold2 5G US 
                ("Samsung SM-G781W", "SDK 33"),         # (Android 13) Samsung Galaxy S20 Fe 5G CA 
                ("Samsung SM-N981N", "SDK 33"),         # (Android 13) Samsung Galaxy Note 20 5G KR 
                ("Samsung SM-N986N", "SDK 33"),         # (Android 13) Samsung Galaxy Note 20 Ultra UW 5G KR 
                ("Samsung SM-F916J", "SDK 33"),         # (Android 13) Samsung Galaxy Z Fold2 UW 5G JP 
                ("Samsung SM-N981W", "SDK 33"),         # (Android 13) Samsung Galaxy Note 20 5G CA 
                ("Samsung SM-N986W", "SDK 33"),         # (Android 13) Samsung Galaxy Note 20 Ultra 5G CA 
                ("Samsung SM-N9810", "SDK 33"),         # (Android 13) Samsung Galaxy Note 20 5G CN 
                ("Samsung SM-N986U", "SDK 33"),         # (Android 13) Samsung Galaxy Note 20 Ultra UW 5G US 
                ("Samsung SM-A516D", "SDK 33"),         # (Android 13) Samsung Galaxy A51 5G JP 
                ("Samsung SM-N986C", "SDK 33"),         # (Android 13) Samsung Galaxy Note 20 Ultra 5G JP 
                ("Samsung SM-N986D", "SDK 33"),         # (Android 13) Samsung Galaxy Note 20 Ultra UW 5G JP 
                ("Samsung SM-A516J", "SDK 33"),         # (Android 13) Samsung Galaxy A51 5G JP 
                ("Samsung SM-F916N", "SDK 33"),         # (Android 13) Samsung Galaxy Z Fold2 UW 5G KR 
                ("Samsung SM-N986J", "SDK 33"),         # (Android 13) Samsung Galaxy Note 20 Ultra UW 5G JP 
                ("Samsung SM-N981U", "SDK 33"),         # (Android 13) Samsung Galaxy Note 20 5G US 
                ("Samsung SM-N981U1", "SDK 33"),        # (Android 13) Samsung Galaxy Note 20 5G US 
                ("Samsung SM-N980F", "SDK 33"),         # (Android 13) Samsung Galaxy Note 20 Global 
                ("Samsung SM-N981B", "SDK 33"),         # (Android 13) Samsung Galaxy Note 20 5G Global 
                ("Samsung SM-N986U1", "SDK 33"),        # (Android 13) Samsung Galaxy Note 20 Ultra 5G US 
                ("Samsung SM-N9860", "SDK 33"),         # (Android 13) Samsung Galaxy Note 20 Ultra 5G CN 
                ("Samsung SM-N985F", "SDK 33"),         # (Android 13) Samsung Galaxy Note 20 Ultra Global 
                ("Samsung SM-N986B", "SDK 33"),         # (Android 13) Samsung Galaxy Note 20 Ultra 5G Global 
                ("Samsung SM-M3070", "SDK 31"),         # (Android 12) Samsung Galaxy M30S CN 
                ("Samsung SM-A5070", "SDK 31"),         # (Android 12) Samsung Galaxy A50S CN 
                ("Samsung SM-A5160", "SDK 33"),         # (Android 13) Samsung Galaxy A51 5G CN 
                ("Samsung SM-F707U", "SDK 33"),         # (Android 13) Samsung Galaxy Z Flip 5G US 
                ("Samsung SM-F707U1", "SDK 33"),        # (Android 13) Samsung Galaxy Z Flip 5G Na 
                ("Samsung SM-F707B", "SDK 33"),         # (Android 13) Samsung Galaxy Z Flip 5G Global 
                ("Samsung SM-F7070", "SDK 33"),         # (Android 13) Samsung Galaxy Z Flip 5G CN 
                ("Samsung SM-G770U1", "SDK 33"),        # (Android 13) Samsung Galaxy S10 Lite US 
                ("Samsung SM-M017F", "SDK 31"),         # (Android 12) Samsung Galaxy M01S Global 
                ("Samsung SM-A716B", "SDK 33"),         # (Android 13) Samsung Galaxy A71 5G Global 
                ("Samsung SM-G986N", "SDK 33"),         # (Android 13) Samsung Galaxy S20+ 5G KR 
                ("Samsung SM-G986B", "SDK 33"),         # (Android 13) Samsung Galaxy S20+ 5G Global 
                ("Samsung SM-G985F", "SDK 33"),         # (Android 13) Samsung Galaxy S20+ Global 
                ("Samsung SM-G986U1", "SDK 33"),        # (Android 13) Samsung Galaxy S20+ 5G US 
                ("Samsung SM-G986J", "SDK 33"),         # (Android 13) Samsung Galaxy S20+ 5G JP 
                ("Samsung SM-F707J", "SDK 33"),         # (Android 13) Samsung Galaxy Z Flip 5G JP 
                ("Samsung SM-A115F", "SDK 33"),         # (Android 13) Samsung Galaxy A11 Global 
                ("Samsung SM-A215U1", "SDK 33"),        # (Android 13) Samsung Galaxy A21 US 
                ("Samsung SM-A215W", "SDK 33"),         # (Android 13) Samsung Galaxy A21 CA 
                ("Samsung SM-F707N", "SDK 33"),         # (Android 13) Samsung Galaxy Z Flip 5G KR 
                ("Samsung SM-F700N", "SDK 33"),         # (Android 13) Samsung Galaxy Z Flip KR 
                ("Samsung SM-G988Q", "SDK 33"),         # (Android 13) Samsung Galaxy S20 Ultra 5G JP 
                ("Samsung SM-M015F", "SDK 33"),         # (Android 13) Samsung Galaxy M01 Global 
                ("Samsung SM-M015G", "SDK 33"),         # (Android 13) Samsung Galaxy M01 
                ("Samsung SM-M115F", "SDK 33"),         # (Android 13) Samsung Galaxy M11 Global 
                ("Samsung SM-G988W", "SDK 33"),         # (Android 13) Samsung Galaxy S20 Ultra 5G CA 
                ("Samsung SM-G9880", "SDK 33"),         # (Android 13) Samsung Galaxy S20 Ultra 5G CN HK 
                ("Samsung SM-G9860", "SDK 33"),         # (Android 13) Samsung Galaxy S20+ 5G CN HK 
                ("Samsung SM-G9810", "SDK 33"),         # (Android 13) Samsung Galaxy S20 5G CN HK 
                ("Samsung SM-G988U1", "SDK 33"),        # (Android 13) Samsung Galaxy S20 Ultra 5G US 
                ("Samsung SM-G988U", "SDK 33"),         # (Android 13) Samsung Galaxy S20 Ultra 5G US 
                ("Samsung SM-G988N", "SDK 33"),         # (Android 13) Samsung Galaxy S20 Ultra 5G KR 
                ("Samsung SM-G986W", "SDK 33"),         # (Android 13) Samsung Galaxy S20+ 5G CA 
                ("Samsung SM-G986U", "SDK 33"),         # (Android 13) Samsung Galaxy S20+ 5G US 
                ("Samsung SM-G980F", "SDK 33"),         # (Android 13) Samsung Galaxy S20 Global 
                ("Samsung SM-G981B", "SDK 33"),         # (Android 13) Samsung Galaxy S20 5G Global 
                ("Samsung SM-G981W", "SDK 33"),         # (Android 13) Samsung Galaxy S20 5G CA 
                ("Samsung SM-G981U", "SDK 33"),         # (Android 13) Samsung Galaxy S20 5G UW US 
                ("Samsung SM-G981U1", "SDK 33"),        # (Android 13) Samsung Galaxy S20 5G US 
                ("Samsung SM-M215F", "SDK 33"),         # (Android 13) Samsung Galaxy M21 Global 
                ("Samsung SM-A415D", "SDK 33"),         # (Android 13) Samsung Galaxy A41 JP 
                ("Samsung SM-A515U1", "SDK 33"),        # (Android 13) Samsung Galaxy A51 US 
                ("Samsung SM-A515U", "SDK 33"),         # (Android 13) Samsung Galaxy A51 US 
                ("Samsung SM-A516N", "SDK 33"),         # (Android 13) Samsung Galaxy A51 5G KR 
                ("Samsung SM-A307GT", "SDK 31"),        # (Android 12) Samsung Galaxy A30S Dtv Br 
                ("Samsung SM-A307GN", "SDK 31"),        # (Android 12) Samsung Galaxy A30S Na 
                ("Samsung SM-A415J", "SDK 33"),         # (Android 13) Samsung Galaxy A41 Wimax 2+ 
                ("Samsung SM-G986", "SDK 33"),          # (Android 13) Samsung Galaxy S20+ 5G UW JP 
                ("Samsung SM-F700U", "SDK 33"),         # (Android 13) Samsung Galaxy Z Flip US 
                ("Samsung SM-A415F", "SDK 33"),         # (Android 13) Samsung Galaxy A41 Global 
                ("Samsung SM-F700J", "SDK 33"),         # (Android 13) Samsung Galaxy Z Flip 
                ("Samsung SM-G981J", "SDK 33"),         # (Android 13) Samsung Galaxy S20 5G JP 
                ("Samsung SM-G981D", "SDK 33"),         # (Android 13) Samsung Galaxy S20 5G JP 
                ("Samsung SM-G981N", "SDK 33"),         # (Android 13) Samsung Galaxy S20 5G KR 
                ("Samsung SM-G770F", "SDK 33"),         # (Android 13) Samsung Galaxy S10 Lite IN 
                ("Samsung SM-F700F", "SDK 33"),         # (Android 13) Samsung Galaxy Z Flip Global 
                ("Samsung SM-A7160", "SDK 33"),         # (Android 13) Samsung Galaxy A71 5G CN 
                ("Samsung SM-A015V", "SDK 31"),         # (Android 12) Samsung Galaxy A01 US 
                ("Samsung SM-A015M", "SDK 31"),         # (Android 12) Samsung Galaxy A01 LATAM 
                ("Samsung SM-A015G", "SDK 31"),         # (Android 12) Samsung Galaxy A01 
                ("Samsung SM-A515FN", "SDK 33"),        # (Android 13) Samsung Galaxy A51 Global 
                ("Samsung SM-A015F", "SDK 31"),         # (Android 12) Samsung Galaxy A01 Global 
                ("Samsung SM-N770F", "SDK 33"),         # (Android 13) Samsung Galaxy Note 10 Lite 
                ("Samsung SM-A102N", "SDK 31"),         # (Android 12) Samsung Galaxy A10E KR 
                ("Samsung SM-W2020", "SDK 31"),         # (Android 12) Samsung W20 5G CN 
                ("Samsung SM-A307FN", "SDK 31"),        # (Android 12) Samsung Galaxy A30S EMEA IN 
                ("Samsung SM-N975D", "SDK 31"),         # (Android 12) Samsung Galaxy Note 10+ Star Wars JP 
                ("Samsung SM-F900U1", "SDK 31"),        # (Android 12) Samsung Galaxy Fold US 
                ("Samsung SM-M107F", "SDK 31"),         # (Android 12) Samsung Galaxy M10S Global 
                ("Samsung SM-A202D", "SDK 31"),         # (Android 12) Samsung Galaxy A20 JP 
                ("Samsung SM-A107M", "SDK 31"),         # (Android 12) Samsung Galaxy A10S LATAM 
                ("Samsung SM-A107F", "SDK 31"),         # (Android 12) Samsung Galaxy A10S Global 
                ("Samsung SM-N975F", "SDK 31"),         # (Android 12) Samsung Galaxy Note 10+ Global 
                ("Samsung SM-N976T", "SDK 33"),         # (Android 13) Samsung Galaxy Note 10+ 5G US 
                ("Samsung SM-G889F", "SDK 29"),         # (Android 10) Samsung Galaxy Xcover Fieldpro Global 
                ("Samsung SM-A705W", "SDK 31"),         # (Android 12) Samsung Galaxy A70 CA 
                ("Samsung SM-A505W", "SDK 31"),         # (Android 12) Samsung Galaxy A50 CA 
                ("Samsung SM-G977D", "SDK 31"),         # (Android 12) Samsung Galaxy S10 5G JP 
                ("Samsung SM-N975U1", "SDK 31"),        # (Android 12) Samsung Galaxy Note 10+ Star Wars US 
                ("Samsung SM-M307F", "SDK 31"),         # (Android 12) Samsung Galaxy M30S Global 
                ("Samsung SM-A7070", "SDK 31"),         # (Android 12) Samsung Galaxy A70S CN 
                ("Samsung SM-N975C", "SDK 33"),         # (Android 13) Samsung Galaxy Note 10+ JP 
                ("Samsung SM-N975J", "SDK 31"),         # (Android 12) Samsung Galaxy Note 10+ Wimax 2+ 
                ("Samsung SM-G973C", "SDK 33"),         # (Android 13) Samsung Galaxy S10 JP 
                ("Samsung SM-A102U1", "SDK 31"),        # (Android 12) Samsung Galaxy A10E US 
                ("Samsung SM-A202J", "SDK 31"),         # (Android 12) Samsung Galaxy A20 Wimax 2+ 
                ("Samsung SM-F900J", "SDK 31"),         # (Android 12) Samsung Galaxy Fold Wimax 2+ 
                ("Samsung SM-F9000", "SDK 31"),         # (Android 12) Samsung Galaxy Fold CN 
                ("Samsung SM-A2070", "SDK 31"),         # (Android 12) Samsung Galaxy A20S CN 
                ("Samsung SM-A207F", "SDK 31"),         # (Android 12) Samsung Galaxy A20S Global 
                ("Samsung SM-F907N", "SDK 31"),         # (Android 12) Samsung Galaxy Fold 5G KR 
                ("Samsung SM-F907B", "SDK 31"),         # (Android 12) Samsung Galaxy Fold 5G Global 
                ("Samsung SM-F900U", "SDK 31"),         # (Android 12) Samsung Galaxy Fold US 
                ("Samsung SM-A105G", "SDK 31"),         # (Android 12) Samsung Galaxy A10 
                ("Samsung SM-A105N", "SDK 31"),         # (Android 12) Samsung Galaxy A10 KR 
                ("Samsung SM-A105FN", "SDK 31"),        # (Android 12) Samsung Galaxy A10 Global 
                ("Samsung SM-A7050", "SDK 31"),         # (Android 12) Samsung Galaxy A70 
                ("Samsung SM-A9080", "SDK 31"),         # (Android 12) Samsung Galaxy A90 5G CN 
                ("Samsung SM-A305N", "SDK 31"),         # (Android 12) Samsung Galaxy A30 KR 
                ("Samsung SM-A505N", "SDK 31"),         # (Android 12) Samsung Galaxy A50 KR 
                ("Samsung SM-A908N", "SDK 31"),         # (Android 12) Samsung Galaxy A90 5G KR 
                ("Samsung SM-A908B", "SDK 31"),         # (Android 12) Samsung Galaxy A90 5G Global 
                ("Samsung SM-A705MN", "SDK 31"),        # (Android 12) Samsung Galaxy A70 Am 
                ("Samsung SM-A705YN", "SDK 31"),        # (Android 12) Samsung Galaxy A70 AU 
                ("Samsung SM-A707F", "SDK 31"),         # (Android 12) Samsung Galaxy A70S Global 
                ("Samsung SM-A505YN", "SDK 31"),        # (Android 12) Samsung Galaxy A50 AU 
                ("Samsung SM-A505U1", "SDK 31"),        # (Android 12) Samsung Galaxy A50 US 
                ("Samsung SM-A750C", "SDK 31"),         # (Android 12) Samsung Galaxy A7 Duos JP 
                ("Samsung SM-A507FN", "SDK 31"),        # (Android 12) Samsung Galaxy A50S Global 
                ("Samsung SM-N976V", "SDK 31"),         # (Android 12) Samsung Galaxy Note 10+ 5G US 
                ("Samsung SM-N976B", "SDK 31"),         # (Android 12) Samsung Galaxy Note 10+ 5G Global 
                ("Samsung SM-N9750", "SDK 31"),         # (Android 12) Samsung Galaxy Note 10+ CN 
                ("Samsung SM-N9700", "SDK 31"),         # (Android 12) Samsung Galaxy Note 10 CN TW 
                ("Samsung SM-N970U1", "SDK 31"),        # (Android 12) Samsung Galaxy Note 10 US 
                ("Samsung SM-N9760", "SDK 31"),         # (Android 12) Samsung Galaxy Note 10+ 5G CN 
                ("Samsung SM-N976N", "SDK 31"),         # (Android 12) Samsung Galaxy Note 10+ 5G KR 
                ("Samsung SM-N971N", "SDK 31"),         # (Android 12) Samsung Galaxy Note 10 5G KR 
                ("Samsung SM-N970F", "SDK 31"),         # (Android 12) Samsung Galaxy Note 10 Global 
                ("Samsung SM-N975W", "SDK 31"),         # (Android 12) Samsung Galaxy Note 10+ CA 
                ("Samsung SM-N970W", "SDK 31"),         # (Android 12) Samsung Galaxy Note 10 CA 
                ("Samsung SM-N975U", "SDK 31"),         # (Android 12) Samsung Galaxy Note 10+ US 
                ("Samsung SM-N970U", "SDK 31"),         # (Android 12) Samsung Galaxy Note 10 US 
                ("Samsung SM-G977U", "SDK 31"),         # (Android 12) Samsung Galaxy S10 5G US 
                ("Samsung SM-G975W", "SDK 31"),         # (Android 12) Samsung Galaxy S10+ CA 
                ("Samsung SM-G975U1", "SDK 31"),        # (Android 12) Samsung Galaxy S10+ US 
                ("Samsung SM-G975U", "SDK 31"),         # (Android 12) Samsung Galaxy S10+ Performance Ceramic US 
                ("Samsung SM-G9750", "SDK 31"),         # (Android 12) Samsung Galaxy S10+ Performance Ceramic CN 
                ("Samsung SM-G9758", "SDK 31"),         # (Android 12) Samsung Galaxy S10+ CN 
                ("Samsung SM-G975D", "SDK 31"),         # (Android 12) Samsung Galaxy S10+ JP 
                ("Samsung SM-G975F", "SDK 31"),         # (Android 12) Samsung Galaxy S10+ Global 
                ("Samsung SM-G9738", "SDK 31"),         # (Android 12) Samsung Galaxy S10 4G+ CN 
                ("Samsung SM-G9730", "SDK 31"),         # (Android 12) Samsung Galaxy S10 CN 
                ("Samsung SM-G973W", "SDK 31"),         # (Android 12) Samsung Galaxy S10 CA 
                ("Samsung SM-G973U1", "SDK 31"),        # (Android 12) Samsung Galaxy S10 US 
                ("Samsung SM-G973U", "SDK 31"),         # (Android 12) Samsung Galaxy S10 US 
                ("Samsung SM-G973F", "SDK 31"),         # (Android 12) Samsung Galaxy S10 Global 
                ("Samsung SM-G9708", "SDK 31"),         # (Android 12) Samsung Galaxy S10E 4G+ CN 
                ("Samsung SM-G970N", "SDK 31"),         # (Android 12) Samsung Galaxy S10E KR 
                ("Samsung SM-G977P", "SDK 31"),         # (Android 12) Samsung Galaxy S10 5G US 
                ("Samsung SM-A205W", "SDK 31"),         # (Android 12) Samsung Galaxy A20 CA 
                ("Samsung SM-G970F", "SDK 31"),         # (Android 12) Samsung Galaxy S10E Global 
                ("Samsung SM-G970W", "SDK 31"),         # (Android 12) Samsung Galaxy S10E CA 
                ("Samsung SM-G970U1", "SDK 31"),        # (Android 12) Samsung Galaxy S10E US 
                ("Samsung SM-G970U", "SDK 31"),         # (Android 12) Samsung Galaxy S10E US 
                ("Samsung SM-A505F", "SDK 31"),         # (Android 12) Samsung Galaxy A50 Global 
                ("Samsung SM-A405FM", "SDK 31"),        # (Android 12) Samsung Galaxy A40 Global 
                ("Samsung SM-A202F", "SDK 31"),         # (Android 12) Samsung Galaxy A20E Global 
                ("Samsung SM-A805N", "SDK 31"),         # (Android 12) Samsung Galaxy A80 KR 
                ("Samsung SM-A805F", "SDK 31"),         # (Android 12) Samsung Galaxy A80 Global 
                ("Samsung SM-A8050", "SDK 31"),         # (Android 12) Samsung Galaxy A80 CN 
                ("Samsung SM-M405F", "SDK 31"),         # (Android 12) Samsung Galaxy M40 IN 
                ("Samsung SM-G398FN", "SDK 31"),        # (Android 12) Samsung Galaxy Xcover 4S Global 
                ("Samsung SM-G975J", "SDK 31"),         # (Android 12) Samsung Galaxy S10+ Wimax 2+ JP 
                ("Samsung SM-G973J", "SDK 31"),         # (Android 12) Samsung Galaxy S10 Wimax 2+ JP 
                ("Samsung SM-A305J", "SDK 31"),         # (Android 12) Samsung Galaxy A30 JP 
                ("Samsung SM-G977N", "SDK 31"),         # (Android 12) Samsung Galaxy S10 5G KR 
                ("Samsung SM-G977B", "SDK 31"),         # (Android 12) Samsung Galaxy S10 5G Global 
                ("Samsung SM-A505FM", "SDK 31"),        # (Android 12) Samsung Galaxy A50 Global 
                ("Samsung SM-A505GN", "SDK 31"),        # (Android 12) Samsung Galaxy A50 
                ("Samsung SM-A6060", "SDK 31"),         # (Android 12) Samsung Galaxy A60 CN 
                ("Samsung SM-A3058", "SDK 31"),         # (Android 12) Samsung Galaxy A40S 4G+ CN 
                ("Samsung SM-A3050", "SDK 31"),         # (Android 12) Samsung Galaxy A40S CN 
                ("Samsung SM-A705F", "SDK 31"),         # (Android 12) Samsung Galaxy A70 Global 
                ("Samsung SM-A205GN", "SDK 31"),        # (Android 12) Samsung Galaxy A20 LATAM 
                ("Samsung SM-A405FN", "SDK 31"),        # (Android 12) Samsung Galaxy A40 Global 
                ("Samsung SM-A205F", "SDK 31"),         # (Android 12) Samsung Galaxy A20 Global 
                ("Samsung SM-G9700", "SDK 31"),         # (Android 12) Samsung Galaxy S10E CN 
                ("Samsung SM-G973D", "SDK 31"),         # (Android 12) Samsung Galaxy S10 JP 
                ("Samsung SM-G973N", "SDK 31"),         # (Android 12) Samsung Galaxy S10 KR 
                ("Samsung SM-G975N", "SDK 31"),         # (Android 12) Samsung Galaxy S10+ KR 
                ("Samsung SM-A105F", "SDK 31"),         # (Android 12) Samsung Galaxy A10 Global 
                ("Samsung SM-A305F", "SDK 31"),         # (Android 12) Samsung Galaxy A30 Global 
                ("Samsung SM-A305FN", "SDK 31"),        # (Android 12) Samsung Galaxy A30 EMEA 
                ("Samsung SM-A505FN", "SDK 31"),        # (Android 12) Samsung Galaxy A50 Global 
                ("Samsung SM-F900F", "SDK 31"),         # (Android 12) Samsung Galaxy Fold Global 
                ("Samsung SM-J336AZ", "SDK 29"),        # (Android 10) Samsung Galaxy Sol 3 US 
                ("Samsung SM-A600AZ", "SDK 29"),        # (Android 10) Samsung Galaxy A6 US 
                ("Samsung SM-A920N", "SDK 29"),         # (Android 10) Samsung Galaxy A9 KR 
                ("Samsung SM-A750F", "SDK 29"),         # (Android 10) Samsung Galaxy A7 Duos Global 
                ("Samsung SM-A750FN", "SDK 29"),        # (Android 10) Samsung Galaxy A7 Duos Global 
                ("Samsung SM-A920F", "SDK 29"),         # (Android 10) Samsung Galaxy A9 Global 
                ("Samsung SM-G6200", "SDK 29"),         # (Android 10) Samsung Galaxy A6S CN 
                ("Samsung SM-A9200", "SDK 29"),         # (Android 10) Samsung Galaxy A9S CN 
                ("Samsung SM-A750N", "SDK 29"),         # (Android 10) Samsung Galaxy A7 KR 
                ("Samsung SM-J720M", "SDK 29"),         # (Android 10) Samsung Galaxy J7 Duo Am 
                ("Samsung SM-J720F", "SDK 29"),         # (Android 10) Samsung Galaxy J7 Duo EMEA 
                ("Samsung SM-J400M", "SDK 29"),         # (Android 10) Samsung Galaxy J4 LATAM 
                ("Samsung SM-J400G", "SDK 29"),         # (Android 10) Samsung Galaxy J4 2 Degrees 
                ("Samsung SM-J400F", "SDK 29"),         # (Android 10) Samsung Galaxy J4 Duos Global 
                ("Samsung SM-A605FN", "SDK 29"),        # (Android 10) Samsung Galaxy A6+ Global 
                ("Samsung SM-J600FN", "SDK 29"),        # (Android 10) Samsung Galaxy J6 EMEA 
                ("Samsung SM-A6058", "SDK 29"),         # (Android 10) Samsung Galaxy A9 Star Lite 4G+ Duos CN 
                ("Samsung SM-A605F", "SDK 29"),         # (Android 10) Samsung Galaxy A6+ Duos Global 
                ("Samsung SM-A600F", "SDK 29"),         # (Android 10) Samsung Galaxy A6 Duos Global 
                ("Samsung SM-A600FN", "SDK 29"),        # (Android 10) Samsung Galaxy A6 EU 
                ("Samsung SM-G8858", "SDK 29"),         # (Android 10) Samsung Galaxy A9 Star 4G+ Duos CN 
                ("Samsung SM-G885F", "SDK 29"),         # (Android 10) Samsung Galaxy A8 Star Duos Global 
                ("Samsung SM-G960F", "SDK 29"),         # (Android 10) Samsung Galaxy S9 Duos 
                ("Samsung SM-J600F", "SDK 29"),         # (Android 10) Samsung Galaxy J6 Duos EMEA 
                ("Samsung SM-J737V", "SDK 29"),         # (Android 10) Samsung Galaxy J7 V Xlte 
                ("Samsung SM-J737P", "SDK 29"),         # (Android 10) Samsung Galaxy J7 Refine US 
                ("Samsung SM-J337V", "SDK 29"),         # (Android 10) Samsung Galaxy J3 V Xlte US 
                ("Samsung SM-J737T", "SDK 29"),         # (Android 10) Samsung Galaxy J7 Star 
                ("Samsung SM-J337P", "SDK 29"),         # (Android 10) Samsung Galaxy J3 Achieve US 
                ("Samsung SM-J337AZ", "SDK 29"),        # (Android 10) Samsung Amp Prime 3 US 
                ("Samsung SM-J600L", "SDK 29"),         # (Android 10) Samsung Galaxy J6 KR 
                ("Samsung SM-J600N", "SDK 29"),         # (Android 10) Samsung Galaxy J6 KR 
                ("Samsung SM-A600G", "SDK 29"),         # (Android 10) Samsung Galaxy A6 Duos 
                ("Samsung SM-J810G", "SDK 29"),         # (Android 10) Samsung Galaxy On8 Duos IN 
                ("Samsung SM-A605K", "SDK 29"),         # (Android 10) Samsung Galaxy Jean KR 
                ("Samsung SM-J337T", "SDK 29"),         # (Android 10) Samsung Galaxy J3 Star US 
                ("Samsung SM-G885S", "SDK 29"),         # (Android 10) Samsung Galaxy A9 Star Duos KR 
                ("Samsung SM-J737A", "SDK 29"),         # (Android 10) Samsung Galaxy J7 
                ("Samsung SM-G885Y", "SDK 29"),         # (Android 10) Samsung Galaxy A8 Star Duos 
                ("Samsung SM-J337A", "SDK 29"),         # (Android 10) Samsung Galaxy J3 US 
                ("Samsung SM-G8850", "SDK 29"),         # (Android 10) Samsung Galaxy A9 Star Duos CN 
                ("Samsung SM-A600N", "SDK 29"),         # (Android 10) Samsung Galaxy A6 KR 
                ("Samsung SM-A6050", "SDK 29"),         # (Android 10) Samsung Galaxy A9 Star Lite Duos CN 
                ("Samsung SM-A605G", "SDK 29"),         # (Android 10) Samsung Galaxy A6+ Duos 
                ("Samsung SM-G8750", "SDK 29"),         # (Android 10) Samsung Galaxy S Lite Luxury Duos CN 
                ("Samsung SM-G965U1", "SDK 29"),        # (Android 10) Samsung Galaxy S9+ US 
                ("Samsung SM-G960U1", "SDK 29"),        # (Android 10) Samsung Galaxy S9 US 
                ("Samsung SM-G9650", "SDK 29"),         # (Android 10) Samsung Galaxy S9+ Duos CN 
                ("Samsung SM-G9600", "SDK 29"),         # (Android 10) Samsung Galaxy S9 Duos CN 
                ("Samsung SM-G9608", "SDK 29"),         # (Android 10) Samsung Galaxy S9 Duos 4G+ CN 
                ("Samsung SM-G960J", "SDK 29"),         # (Android 10) Samsung Galaxy S9 Wimax 2+ 
                ("Samsung SM-G965J", "SDK 29"),         # (Android 10) Samsung Galaxy S9+ Wimax 2+ 
                ("Samsung SM-G965F", "SDK 29"),         # (Android 10) Samsung Galaxy S9+ Duos 
                ("Samsung SM-G965N", "SDK 29"),         # (Android 10) Samsung Galaxy S9+ 
                ("Samsung SM-G960N", "SDK 29"),         # (Android 10) Samsung Galaxy S9 
                ("Samsung SM-G960D", "SDK 29"),         # (Android 10) Samsung Galaxy S9 JP 
                ("Samsung SM-G965D", "SDK 29"),         # (Android 10) Samsung Galaxy S9+ JP 
                ("Samsung SM-G965W", "SDK 29"),         # (Android 10) Samsung Galaxy S9+ 
                ("Samsung SM-G960W", "SDK 29"),         # (Android 10) Samsung Galaxy S9 
                ("Samsung SM-G960U", "SDK 29"),         # (Android 10) Samsung Galaxy S9 US 
                ("Samsung SM-G965U", "SDK 29"),         # (Android 10) Samsung Galaxy S9+ US 
                ("Xiaomi 25060RK16C", "SDK 35"),        # (Android 15) Xiaomi Redmi K80 Extreme 5G CN 
                ("Xiaomi 25053RT47C", "SDK 35"),        # (Android 15) Xiaomi Redmi Turbo 4 Pro 5G CN 
                ("Xiaomi 25053PC47G", "SDK 35"),        # (Android 15) Xiaomi Poco F7 5G Global 
                ("Xiaomi 25053PC47I", "SDK 35"),        # (Android 15) Xiaomi Poco F7 5G IN 
                ("Xiaomi 24117RK2CC", "SDK 34"),        # (Android 14) Xiaomi Redmi K80 5G CN 
                ("Xiaomi 24122RKC7C", "SDK 34"),        # (Android 14) Xiaomi Redmi K80 Pro 5G CN 
                ("Xiaomi 24127RK2CC", "SDK 34"),        # (Android 14) Xiaomi Redmi K80 Pro 5G CN 
                ("Xiaomi 24116RACCG", "SDK 34"),        # (Android 14) Xiaomi Redmi Note 14 Pro 4G Global 
                ("Xiaomi 2411DRN47C", "SDK 34"),        # (Android 14) Xiaomi Redmi 14R 5G CN 
                ("Xiaomi 24108PCE2I", "SDK 34"),        # (Android 14) Xiaomi Poco M7 5G IN 
                ("Xiaomi 2411DRN47R", "SDK 34"),        # (Android 14) Xiaomi Redmi 14C 5G JP 
                ("Xiaomi 2411DRN47G", "SDK 34"),        # (Android 14) Xiaomi Redmi 14C 5G Global 
                ("Xiaomi 2411DRN47I", "SDK 34"),        # (Android 14) Xiaomi Redmi 14C 5G IN 
                ("Xiaomi 2412DPC0AG", "SDK 35"),        # (Android 15) Xiaomi Poco X7 Pro 5G Global 
                ("Xiaomi 2412DPC0AI", "SDK 35"),        # (Android 15) Xiaomi Poco X7 Pro 5G IN 
                ("Xiaomi 24129RT7CC", "SDK 35"),        # (Android 15) Xiaomi Redmi Turbo 4 5G CN 
                ("Xiaomi 24069RA21C", "SDK 34"),        # (Android 14) Xiaomi Redmi Turbo 3 5G CN 
                ("Xiaomi 23122PCD1I", "SDK 34"),        # (Android 14) Xiaomi Poco X6 5G IN 
                ("Xiaomi 23122PCD1G", "SDK 34"),        # (Android 14) Xiaomi Poco X6 5G Global 
                ("Xiaomi 24095PCADI", "SDK 34"),        # (Android 14) Xiaomi Poco X7 5G IN 
                ("Xiaomi 24095PCADG", "SDK 34"),        # (Android 14) Xiaomi Poco X7 5G Global 
                ("Xiaomi 24090RA29G", "SDK 34"),        # (Android 14) Xiaomi Redmi Note 14 Pro 5G Global 
                ("Xiaomi 24117RN76L", "SDK 34"),        # (Android 14) Xiaomi Redmi Note 14 4G LATAM 
                ("Xiaomi 24117RN76G", "SDK 34"),        # (Android 14) Xiaomi Redmi Note 14 4G 
                ("Xiaomi 24117RN76O", "SDK 34"),        # (Android 14) Xiaomi Redmi Note 14 4G Nfc 
                ("Xiaomi 24116PCC1I", "SDK 34"),        # (Android 14) Xiaomi Poco C75 5G IN 
                ("Xiaomi 24116RNC1I", "SDK 34"),        # (Android 14) Xiaomi Redmi A4 5G IN 
                ("Xiaomi 24044RN32L", "SDK 34"),        # (Android 14) Xiaomi Redmi A3X 4G LATAM 
                ("Xiaomi 24048RN6CG", "SDK 34"),        # (Android 14) Xiaomi Redmi A3X 4G Global 
                ("Xiaomi 24048RN6CI", "SDK 34"),        # (Android 14) Xiaomi Redmi A3X 4G IN 
                ("Xiaomi 2312BPC51X", "SDK 34"),        # (Android 14) Xiaomi Poco C61 4G Global 
                ("Xiaomi 2312BPC51H", "SDK 34"),        # (Android 14) Xiaomi Poco C61 4G IN 
                ("Xiaomi 2312CRNCCL", "SDK 34"),        # (Android 14) Xiaomi Redmi A3 4G LATAM 
                ("Xiaomi 23129RN51X", "SDK 34"),        # (Android 14) Xiaomi Redmi A3 4G Global 
                ("Xiaomi 23129RN51H", "SDK 34"),        # (Android 14) Xiaomi Redmi A3 4G IN 
                ("Xiaomi 2409BRN2CA", "SDK 34"),        # (Android 14) Xiaomi Redmi 14C 4G Global 
                ("Xiaomi 2409BRN2CL", "SDK 34"),        # (Android 14) Xiaomi Redmi 14C 4G LATAM JP 
                ("Xiaomi 2409BRN2CC", "SDK 34"),        # (Android 14) Xiaomi Redmi 14C 4G CN 
                ("Xiaomi 2410FPCC5G", "SDK 34"),        # (Android 14) Xiaomi Poco C75 4G Nfc Global 
                ("Xiaomi 2409BRN2CG", "SDK 34"),        # (Android 14) Xiaomi Redmi A3 Pro 4G Global 
                ("Xiaomi 2409BRN2CY", "SDK 34"),        # (Android 14) Xiaomi Redmi 14C 4G Nfc Global 
                ("Xiaomi 2409FPCC4G", "SDK 34"),        # (Android 14) Xiaomi Poco M7 Pro 5G Global 
                ("Xiaomi 2409FPCC4I", "SDK 34"),        # (Android 14) Xiaomi Poco M7 Pro 5G IN 
                ("Xiaomi 24094RAD4C", "SDK 34"),        # (Android 14) Xiaomi Redmi Note 14 5G CN 
                ("Xiaomi 24094RAD4G", "SDK 34"),        # (Android 14) Xiaomi Redmi Note 14 5G Global 
                ("Xiaomi 24094RAD4I", "SDK 34"),        # (Android 14) Xiaomi Redmi Note 14 5G IN 
                ("Xiaomi 24115RA8EG", "SDK 34"),        # (Android 14) Xiaomi Redmi Note 14 Pro+ 5G Global 
                ("Xiaomi 24115RA8EC", "SDK 34"),        # (Android 14) Xiaomi Redmi Note 14 Pro+ 5G CN 
                ("Xiaomi 24115RA8EI", "SDK 34"),        # (Android 14) Xiaomi Redmi Note 14 Pro+ 5G IN 
                ("Xiaomi 24090RA29C", "SDK 34"),        # (Android 14) Xiaomi Redmi Note 14 Pro 5G CN 
                ("Xiaomi 24090RA29I", "SDK 34"),        # (Android 14) Xiaomi Redmi Note 14 Pro 5G IN 
                ("Xiaomi 2407FRK8EC", "SDK 34"),        # (Android 14) Xiaomi Redmi K70 Champion Extreme 5G CN 
                ("Xiaomi 24053PY09I", "SDK 34"),        # (Android 14) Xiaomi Mi 14 Civi 5G IN 
                ("Xiaomi 24072PX77C", "SDK 34"),        # (Android 14) Xiaomi Mi Mix Fold 4 5G CN 
                ("Xiaomi 2405CPX3DC", "SDK 34"),        # (Android 14) Xiaomi Mi Mix Flip 5G CN 
                ("Xiaomi 2405CPX3DG", "SDK 34"),        # (Android 14) Xiaomi Mi Mix Flip 5G Global 
                ("Xiaomi 2406APNFAG", "SDK 34"),        # (Android 14) Xiaomi Mi 14T 5G Global 
                ("Xiaomi 2407FPN8EG", "SDK 34"),        # (Android 14) Xiaomi Mi 14T Pro 5G Global 
                ("Xiaomi 2407FPN8ER", "SDK 34"),        # (Android 14) Xiaomi Mi 14T Pro 5G JP 
                ("Xiaomi 24069PC21I", "SDK 34"),        # (Android 14) Xiaomi Poco F6 5G IN 
                ("Xiaomi 24069PC21G", "SDK 34"),        # (Android 14) Xiaomi Poco F6 5G Global 
                ("Xiaomi 2311DRK48I", "SDK 34"),        # (Android 14) Xiaomi Poco X6 Pro 5G Base IN 
                ("Xiaomi 2311DRK48G", "SDK 34"),        # (Android 14) Xiaomi Poco X6 Pro 5G Base Global 
                ("Xiaomi 23113RKC6G", "SDK 34"),        # (Android 14) Xiaomi Poco F6 Pro 5G Global 
                ("Xiaomi 23128PC33I", "SDK 34"),        # (Android 14) Xiaomi Poco M6 5G IN 
                ("Xiaomi 23124RN87C", "SDK 34"),        # (Android 14) Xiaomi Redmi 13R 5G CN 
                ("Xiaomi 2404APC5FG", "SDK 34"),        # (Android 14) Xiaomi Poco M6 4G Nfc Global 
                ("Xiaomi 2404ARN45I", "SDK 34"),        # (Android 14) Xiaomi Redmi 13 4G IN 
                ("Xiaomi 24049RN28L", "SDK 34"),        # (Android 14) Xiaomi Redmi 13 4G LATAM 
                ("Xiaomi 2404APC5FI", "SDK 34"),        # (Android 14) Xiaomi Poco M6 4G IN 
                ("Xiaomi 24040RN64Y", "SDK 34"),        # (Android 14) Xiaomi Redmi 13 4G Nfc Global 
                ("Xiaomi 2404ARN45A", "SDK 34"),        # (Android 14) Xiaomi Redmi 13 4G Global 
                ("Xiaomi 2310FPCA4I", "SDK 34"),        # (Android 14) Xiaomi Poco C65 4G IN 
                ("Xiaomi 2310FPCA4G", "SDK 34"),        # (Android 14) Xiaomi Poco C65 4G Nfc Global 
                ("Xiaomi 23100RN82L", "SDK 34"),        # (Android 14) Xiaomi Redmi 13C 4G LATAM 
                ("Xiaomi 2311DRN14I", "SDK 34"),        # (Android 14) Xiaomi Redmi 13C 4G IN 
                ("Xiaomi 23108RN04Y", "SDK 34"),        # (Android 14) Xiaomi Redmi 13C 4G Nfc Global 
                ("Xiaomi 23106RN0DA", "SDK 34"),        # (Android 14) Xiaomi Redmi 13C 4G Global 
                ("Xiaomi 23129RA5FL", "SDK 34"),        # (Android 14) Xiaomi Redmi Note 13 4G LATAM 
                ("Xiaomi 23124RA7EO", "SDK 34"),        # (Android 14) Xiaomi Redmi Note 13 4G Nfc Global 
                ("Xiaomi 23129RAA4G", "SDK 34"),        # (Android 14) Xiaomi Redmi Note 13 4G Global 
                ("Xiaomi 22312FRAFDI", "SDK 34"),       # (Android 14) Xiaomi Poco X6 Neo 5G IN 
                ("Xiaomi 2311FRAFDC", "SDK 34"),        # (Android 14) Xiaomi Redmi Note 13R Pro 5G CN 
                ("Xiaomi 2312DRAABC", "SDK 34"),        # (Android 14) Xiaomi Redmi Note 13 5G Base CN 
                ("Xiaomi 2312DRAABI", "SDK 34"),        # (Android 14) Xiaomi Redmi Note 13 5G IN 
                ("Xiaomi 2312DRAABG", "SDK 34"),        # (Android 14) Xiaomi Redmi Note 13 5G Base Global 
                ("Xiaomi 23117RA68G", "SDK 34"),        # (Android 14) Xiaomi Redmi Note 13 Pro 4G Global 
                ("Xiaomi 2312FPCA6G", "SDK 34"),        # (Android 14) Xiaomi Poco M6 Pro 4G Global 
                ("Xiaomi 23090RA98C", "SDK 34"),        # (Android 14) Xiaomi Redmi Note 13 Pro+ 5G CN 
                ("Xiaomi 23090RA98I", "SDK 34"),        # (Android 14) Xiaomi Redmi Note 13 Pro+ 5G IN 
                ("Xiaomi 24040RA98R", "SDK 34"),        # (Android 14) Xiaomi Redmi Note 13 Pro+ 5G JP 
                ("Xiaomi 23090RA98G", "SDK 34"),        # (Android 14) Xiaomi Redmi Note 13 Pro+ 5G Global 
                ("Xiaomi 2312DRA50G", "SDK 34"),        # (Android 14) Xiaomi Redmi Note 13 Pro 5G Global 
                ("Xiaomi 2312DRA50I", "SDK 34"),        # (Android 14) Xiaomi Redmi Note 13 Pro 5G IN 
                ("Xiaomi 2312CRAD3C", "SDK 34"),        # (Android 14) Xiaomi Redmi Note 13 Pro 5G CN 
                ("Xiaomi 2312DRA50J", "SDK 34"),        # (Android 14) Xiaomi Redmi Note 13 Pro 5G JP 
                ("Xiaomi 24053PY09C", "SDK 34"),        # (Android 14) Xiaomi Civi 4 Pro 5G CN 
                ("Xiaomi 2311DRK48C", "SDK 34"),        # (Android 14) Xiaomi Redmi K70E 5G CN 
                ("Xiaomi 23113RKC6C", "SDK 34"),        # (Android 14) Xiaomi Redmi K70 5G CN 
                ("Xiaomi 23117RK66C", "SDK 34"),        # (Android 14) Xiaomi Redmi K70 Pro 5G CN 
                ("Xiaomi 23127PN0CC", "SDK 34"),        # (Android 14) Xiaomi Mi 14 5G CN 
                ("Xiaomi 23127PN0CG", "SDK 34"),        # (Android 14) Xiaomi Mi 14 5G Global 
                ("Xiaomi 23116PN5BC", "SDK 34"),        # (Android 14) Xiaomi Mi 14 Pro 5G Titanium CN 
                ("Xiaomi 24031PN0DC", "SDK 34"),        # (Android 14) Xiaomi Mi 14 Ultra 5G CN 
                ("Xiaomi 24030PN60G", "SDK 34"),        # (Android 14) Xiaomi Mi 14 Ultra 5G Global 
                ("Xiaomi 2308CPXD0C", "SDK 34"),        # (Android 14) Xiaomi Mi Mix Fold 3 5G CN 
                ("Xiaomi 2306EPN60G", "SDK 34"),        # (Android 14) Xiaomi Mi 13T 5G Global 
                ("Xiaomi 2306EPN60R", "SDK 34"),        # (Android 14) Xiaomi Mi 13T 5G JP Xig04 
                ("Xiaomi 23088PND5R", "SDK 34"),        # (Android 14) Xiaomi Mi 13T Pro 5G JP 
                ("Xiaomi 23078PND5G", "SDK 34"),        # (Android 14) Xiaomi Mi 13T Pro 5G Global 1Tgb 
                ("Xiaomi 23078RKD5C", "SDK 34"),        # (Android 14) Xiaomi Redmi K60 Extreme Top 5G CN 
                ("Xiaomi 23076PC4BI", "SDK 34"),        # (Android 14) Xiaomi Poco M6 Pro 5G IN 
                ("Xiaomi 23076RA4BR", "SDK 34"),        # (Android 14) Xiaomi Redmi 12 5G JP Xig03 
                ("Xiaomi 23076RN4BI", "SDK 34"),        # (Android 14) Xiaomi Redmi 12 5G IN 
                ("Xiaomi 23076RN8DY", "SDK 34"),        # (Android 14) Xiaomi Redmi 12 5G Global 
                ("Xiaomi 22061218C", "SDK 34"),         # (Android 14) Xiaomi Mi Mix Fold 2 5G CN 
                ("Xiaomi 2304FPN6DC", "SDK 34"),        # (Android 14) Xiaomi Mi 13 Ultra 5G CN 
                ("Xiaomi 2304FPN6DG", "SDK 34"),        # (Android 14) Xiaomi Mi 13 Ultra 5G Global 
                ("Xiaomi 23046PNC9C", "SDK 34"),        # (Android 14) Xiaomi Civi 3 5G CN 
                ("Xiaomi 23054RA19C", "SDK 34"),        # (Android 14) Xiaomi Redmi Note 12T Pro 5G CN 
                ("Xiaomi 23028RA60L", "SDK 34"),        # (Android 14) Xiaomi Redmi Note 12 4G LATAM 
                ("Xiaomi 23021RAA2Y", "SDK 34"),        # (Android 14) Xiaomi Redmi Note 12 4G Nfc Global 
                ("Xiaomi 23021RAA2G", "SDK 34"),        # (Android 14) Xiaomi Redmi Note 12 4G Global 
                ("Xiaomi 23027RAD4I", "SDK 34"),        # (Android 14) Xiaomi Redmi Note 12 4G IN 
                ("Xiaomi 23076RA4BC", "SDK 34"),        # (Android 14) Xiaomi Redmi Note 12R 5G CN 
                ("Xiaomi 2209116AG", "SDK 33"),         # (Android 13) Xiaomi Redmi Note 12 Pro 4G Global 
                ("Xiaomi 23013RK75G", "SDK 34"),        # (Android 14) Xiaomi Poco F5 Pro 5G Global 
                ("Xiaomi 22101317C", "SDK 34"),         # (Android 14) Xiaomi Redmi Note 12R Pro 5G CN 
                ("Xiaomi 23049PCD8G", "SDK 34"),        # (Android 14) Xiaomi Poco F5 5G Global 
                ("Xiaomi 23049RAD8C", "SDK 34"),        # (Android 14) Xiaomi Redmi Note 12 Turbo 5G CN 
                ("Xiaomi 23049PCD8I", "SDK 34"),        # (Android 14) Xiaomi Poco F5 5G IN 
                ("Xiaomi 22101320C", "SDK 34"),         # (Android 14) Xiaomi Redmi Note 12 Pro Speed 5G CN 
                ("Xiaomi 22101316I", "SDK 34"),         # (Android 14) Xiaomi Redmi Note 12 Pro 5G IN 
                ("Xiaomi 22101316C", "SDK 34"),         # (Android 14) Xiaomi Redmi Note 12 Pro 5G CN 
                ("Xiaomi 22101316G", "SDK 34"),         # (Android 14) Xiaomi Redmi Note 12 Pro 5G Global 
                ("Xiaomi 22101316UP", "SDK 34"),        # (Android 14) Xiaomi Redmi Note 12 Pro+ 5G IN 
                ("Xiaomi 22101316UC", "SDK 34"),        # (Android 14) Xiaomi Redmi Note 12 5G CN 
                ("Xiaomi 22101316UCP", "SDK 34"),       # (Android 14) Xiaomi Redmi Note 12 5G CN 
                ("Xiaomi 22101316UG", "SDK 34"),        # (Android 14) Xiaomi Redmi Note 12 Pro+ 5G Global 
                ("Xiaomi 22120RN86G", "SDK 34"),        # (Android 14) Xiaomi Redmi 12C Global 
                ("Xiaomi 22127PC95I", "SDK 34"),        # (Android 14) Xiaomi Poco C55 IN 
                ("Xiaomi 22120RN86I", "SDK 34"),        # (Android 14) Xiaomi Redmi 12C IN 
                ("Xiaomi 22126RN91Y", "SDK 34"),        # (Android 14) Xiaomi Redmi 12C Nfc Global 
                ("Xiaomi 2212ARNC4L", "SDK 34"),        # (Android 14) Xiaomi Redmi 12C LATAM JP 
                ("Xiaomi 22120RN86C", "SDK 34"),        # (Android 14) Xiaomi Redmi 12C CN 
                ("Xiaomi 22111317I", "SDK 34"),         # (Android 14) Xiaomi Redmi Note 12 5G Base IN 
                ("Xiaomi 22111317G", "SDK 34"),         # (Android 14) Xiaomi Redmi Note 12 5G Global 
                ("Xiaomi 22111317PI", "SDK 34"),        # (Android 14) Xiaomi Poco X5 5G IN 
                ("Xiaomi 22111317PG", "SDK 34"),        # (Android 14) Xiaomi Poco X5 5G Global 
                ("Xiaomi 22101320I", "SDK 34"),         # (Android 14) Xiaomi Poco X5 Pro 5G IN 
                ("Xiaomi 22101320G", "SDK 34"),         # (Android 14) Xiaomi Poco X5 Pro 5G Global 
                ("Xiaomi 2210129SC", "SDK 34"),         # (Android 14) Xiaomi Civi 2 5G Hello Kitty CN 
                ("Xiaomi 2210129SG", "SDK 34"),         # (Android 14) Xiaomi Mi 13 Lite 5G Global 
                ("Xiaomi 22081212C", "SDK 34"),         # (Android 14) Xiaomi Redmi K50 Extreme Mercedes-Amg F1 Team 5G CN 
                ("Xiaomi 22122RK93C", "SDK 34"),        # (Android 14) Xiaomi Redmi K60E 5G CN 
                ("Xiaomi 23013RK75C", "SDK 34"),        # (Android 14) Xiaomi Redmi K60 5G CN 
                ("Xiaomi 22127RK46C", "SDK 34"),        # (Android 14) Xiaomi Redmi K60 Pro 5G CN 
                ("Xiaomi 2211133C", "SDK 34"),          # (Android 14) Xiaomi Mi 13 5G CN 
                ("Xiaomi 2211133G", "SDK 34"),          # (Android 14) Xiaomi Mi 13 5G Global 
                ("Xiaomi 22071212AG", "SDK 34"),        # (Android 14) Xiaomi Mi 12T 5G Global 
                ("Xiaomi 22095RA98C", "SDK 34"),        # (Android 14) Xiaomi Redmi Note 11R 5G CN 
                ("Xiaomi 22200414R", "SDK 34"),         # (Android 14) Xiaomi Mi 12T Pro 5G JP 
                ("Xiaomi 22081212R", "SDK 34"),         # (Android 14) Xiaomi Mi 12T Pro 5G JP 
                ("Xiaomi 2210132G", "SDK 34"),          # (Android 14) Xiaomi Mi 13 Pro 5G Global 
                ("Xiaomi 2210132C", "SDK 34"),          # (Android 14) Xiaomi Mi 13 Pro 5G CN 
                ("Xiaomi 22081212UG", "SDK 34"),        # (Android 14) Xiaomi Mi 12T Pro 5G Global 
                ("Xiaomi 2207122MC", "SDK 34"),         # (Android 14) Xiaomi Mi 12 Pro 5G CN 
                ("Xiaomi 2203121C", "SDK 34"),          # (Android 14) Xiaomi Mi 12S Ultra 5G CN 
                ("Xiaomi 2206122SC", "SDK 34"),         # (Android 14) Xiaomi Mi 12S Pro 5G CN 
                ("Xiaomi 2206123SC", "SDK 34"),         # (Android 14) Xiaomi Mi 12S 5G CN 
                ("Xiaomi 220333QPI", "SDK 33"),         # (Android 13) Xiaomi Poco C40 IN 
                ("Xiaomi 220333QPG", "SDK 33"),         # (Android 13) Xiaomi Poco C40 Global 
                ("Xiaomi 2109119BC", "SDK 34"),         # (Android 14) Xiaomi Civi 1S 5G CN 
                ("Xiaomi 22011119TI", "SDK 33"),        # (Android 13) Xiaomi Redmi 10 Prime IN 
                ("Xiaomi 22071219AI", "SDK 34"),        # (Android 14) Xiaomi Redmi 11 Prime 4G IN 
                ("Xiaomi 22071219CI", "SDK 34"),        # (Android 14) Xiaomi Poco M5 IN 
                ("Xiaomi 22071219CG", "SDK 34"),        # (Android 14) Xiaomi Poco M5 Global 
                ("Xiaomi 22021211RI", "SDK 34"),        # (Android 14) Xiaomi Poco F4 5G IN 
                ("Xiaomi 22021211RG", "SDK 34"),        # (Android 14) Xiaomi Poco F4 5G Global 
                ("Xiaomi 21121210I", "SDK 34"),         # (Android 14) Xiaomi Poco F4 Gt 5G IN 
                ("Xiaomi 2207117BPG", "SDK 34"),        # (Android 14) Xiaomi Poco M5S Global 
                ("Xiaomi M2101K7BNY", "SDK 33"),        # (Android 13) Xiaomi Redmi Note 10S Nfc Global 
                ("Xiaomi M2101K7BL", "SDK 33"),         # (Android 13) Xiaomi Redmi Note 10S LATAM 
                ("Xiaomi M2101K7BI", "SDK 33"),         # (Android 13) Xiaomi Redmi Note 11 Se IN 
                ("Xiaomi M2103K19C", "SDK 33"),         # (Android 13) Xiaomi Redmi Note 11Se 5G CN 
                ("Xiaomi 22041216UC", "SDK 34"),        # (Android 14) Xiaomi Redmi Note 11T Pro+ 5G CN 
                ("Xiaomi 22041216C", "SDK 34"),         # (Android 14) Xiaomi Redmi Note 11T Pro 5G CN 
                ("Xiaomi 22041216I", "SDK 34"),         # (Android 14) Xiaomi Redmi K50I 5G IN 
                ("Xiaomi 22041216G", "SDK 34"),         # (Android 14) Xiaomi Poco X4 Gt 5G Global 
                ("Xiaomi 2201116PI", "SDK 33"),         # (Android 13) Xiaomi Poco X4 Pro 5G IN 
                ("Xiaomi 2201116PG", "SDK 33"),         # (Android 13) Xiaomi Poco X4 Pro 5G Global 
                ("Xiaomi 220333QBI", "SDK 33"),         # (Android 13) Xiaomi Redmi 10 Power 4G IN 
                ("Xiaomi 220233L2I", "SDK 33"),         # (Android 13) Xiaomi Redmi 10A IN 
                ("Xiaomi 220233L2G", "SDK 33"),         # (Android 13) Xiaomi Redmi 10A Global 
                ("Xiaomi 220233L2C", "SDK 33"),         # (Android 13) Xiaomi Redmi 10A CN 
                ("Xiaomi 21121210C", "SDK 34"),         # (Android 14) Xiaomi Redmi K50 Gaming 5G 
                ("Xiaomi 21121210G", "SDK 34"),         # (Android 14) Xiaomi Poco F4 Gt 5G Global 
                ("Xiaomi 22041211AC", "SDK 34"),        # (Android 14) Xiaomi Redmi K50 5G CN 
                ("Xiaomi 22011211C", "SDK 34"),         # (Android 14) Xiaomi Redmi K50 Pro 5G CN 
                ("Xiaomi 220333QAG", "SDK 33"),         # (Android 13) Xiaomi Redmi 10C 4G Global 
                ("Xiaomi 220333QNY", "SDK 33"),         # (Android 13) Xiaomi Redmi 10C 4G Nfc Global 
                ("Xiaomi 22041219G", "SDK 34"),         # (Android 14) Xiaomi Redmi 10 5G Global 
                ("Xiaomi 22041219C", "SDK 34"),         # (Android 14) Xiaomi Redmi Note 11E 5G CN 
                ("Xiaomi 22041219I", "SDK 34"),         # (Android 14) Xiaomi Redmi 11 Prime 5G IN 
                ("Xiaomi 22041219PI", "SDK 34"),        # (Android 14) Xiaomi Poco M4 5G IN 
                ("Xiaomi 22041219PG", "SDK 34"),        # (Android 14) Xiaomi Poco M4 5G Global 
                ("Xiaomi 2203129I", "SDK 34"),          # (Android 14) Xiaomi Mi 12 Lite 5G Global 
                ("Xiaomi 2203129G", "SDK 34"),          # (Android 14) Xiaomi Mi 12 Lite 5G Global 
                ("Xiaomi 2112123AC", "SDK 33"),         # (Android 13) Xiaomi Mi 12X 5G CN 
                ("Xiaomi 2112123AG", "SDK 33"),         # (Android 13) Xiaomi Mi 12X 5G Global 
                ("Xiaomi 2201123G", "SDK 34"),          # (Android 14) Xiaomi Mi 12 5G Global 
                ("Xiaomi 2201122G", "SDK 34"),          # (Android 14) Xiaomi Mi 12 Pro 5G Global 
                ("Xiaomi 2201123C", "SDK 34"),          # (Android 14) Xiaomi Mi 12 5G CN 
                ("Xiaomi 2201122C", "SDK 34"),          # (Android 14) Xiaomi Mi 12 Pro 5G CN 
                ("Xiaomi 22031116BG", "SDK 33"),        # (Android 13) Xiaomi Redmi Note 11S 5G Global 
                ("Xiaomi M2006C3MII", "SDK 33"),        # (Android 13) Xiaomi Redmi 9 Activ IN 
                ("Xiaomi 21091116C", "SDK 33"),         # (Android 13) Xiaomi Redmi Note 11 Pro 5G CN 
                ("Xiaomi 21091116I", "SDK 33"),         # (Android 13) Xiaomi Redmi Note 11I 5G IN 
                ("Xiaomi 21091116UC", "SDK 33"),        # (Android 13) Xiaomi Redmi Note 11 Pro+ 5G CN 
                ("Xiaomi 21091116UI", "SDK 33"),        # (Android 13) Xiaomi Redmi Note 11I Hypercharge 5G IN 
                ("Xiaomi 21091116UG", "SDK 33"),        # (Android 13) Xiaomi Redmi Note 11 Pro+ 5G Global 
                ("Xiaomi M2006C3LI", "SDK 33"),         # (Android 13) Xiaomi Redmi 9A Sport IN 
                ("Xiaomi 2107113SI", "SDK 33"),         # (Android 13) Xiaomi Mi 11T Pro 5G IN 
                ("Xiaomi 2107113SR", "SDK 33"),         # (Android 13) Xiaomi Mi 11T Pro 5G JP 
                ("Xiaomi 2201116SI", "SDK 33"),         # (Android 13) Xiaomi Redmi Note 11 Pro+ 5G IN 
                ("Xiaomi M2006C3LII", "SDK 33"),        # (Android 13) Xiaomi Redmi 9I Sport IN 
                ("Xiaomi 2201116SR", "SDK 33"),         # (Android 13) Xiaomi Redmi Note 11 Pro 5G JP 
                ("Xiaomi 21091116AC", "SDK 33"),        # (Android 13) Xiaomi Redmi Note 11 5G CN 
                ("Xiaomi 21091116AG", "SDK 33"),        # (Android 13) Xiaomi Poco M4 Pro 5G Global 
                ("Xiaomi 21091116AI", "SDK 33"),        # (Android 13) Xiaomi Redmi Note 11T 5G IN 
                ("Xiaomi 21121119SC", "SDK 33"),        # (Android 13) Xiaomi Redmi Note 11 4G CN 
                ("Xiaomi 21121119SG", "SDK 33"),        # (Android 13) Xiaomi Redmi 10 Global 
                ("Xiaomi 2201117TI", "SDK 33"),         # (Android 13) Xiaomi Redmi Note 11 4G IN 
                ("Xiaomi 2201117TL", "SDK 33"),         # (Android 13) Xiaomi Redmi Note 11 4G LATAM JP 
                ("Xiaomi 2201117TG", "SDK 33"),         # (Android 13) Xiaomi Redmi Note 11 4G Global 
                ("Xiaomi 2201117TY", "SDK 33"),         # (Android 13) Xiaomi Redmi Note 11 4G Global 
                ("Xiaomi 2201117PI", "SDK 33"),         # (Android 13) Xiaomi Poco M4 Pro 4G IN 
                ("Xiaomi 2201117PG", "SDK 33"),         # (Android 13) Xiaomi Poco M4 Pro 4G Global 
                ("Xiaomi 2201117SY", "SDK 33"),         # (Android 13) Xiaomi Redmi Note 11S 4G Global 
                ("Xiaomi 2201117SL", "SDK 33"),         # (Android 13) Xiaomi Redmi Note 11S 4G LATAM 
                ("Xiaomi 2201117SG", "SDK 33"),         # (Android 13) Xiaomi Redmi Note 11S 4G Global 
                ("Xiaomi 2201117SI", "SDK 33"),         # (Android 13) Xiaomi Redmi Note 11S 4G IN 
                ("Xiaomi 2109106A1I", "SDK 33"),        # (Android 13) Xiaomi Redmi Note 10 Lite IN 
                ("Xiaomi 2201116TG", "SDK 33"),         # (Android 13) Xiaomi Redmi Note 11 Pro 4G Global 
                ("Xiaomi 2201116SG", "SDK 33"),         # (Android 13) Xiaomi Redmi Note 11 Pro 5G Global 
                ("Xiaomi 21061119DG", "SDK 33"),        # (Android 13) Xiaomi Redmi 10 Global 
                ("Xiaomi 21061119AL", "SDK 33"),        # (Android 13) Xiaomi Redmi 10 LATAM 
                ("Xiaomi 2107119DC", "SDK 33"),         # (Android 13) Xiaomi Mi 11 Youth Vitality 5G CN 
                ("Xiaomi 2109119DI", "SDK 33"),         # (Android 13) Xiaomi Mi 11 Lite Ne 5G IN 
                ("Xiaomi 2109119DG", "SDK 33"),         # (Android 13) Xiaomi Mi 11 Lite 5G Ne Global 
                ("Xiaomi 21081111RG", "SDK 33"),        # (Android 13) Xiaomi Mi 11T 5G Global 
                ("Xiaomi 2107113SG", "SDK 33"),         # (Android 13) Xiaomi Mi 11T Pro 5G Global 
                ("Xiaomi M2004J19PI", "SDK 33"),        # (Android 13) Xiaomi Poco M2 Reloaded IN 
                ("Xiaomi 21061110AG", "SDK 33"),        # (Android 13) Xiaomi Poco X3 Gt 5G Global 
                ("Xiaomi 21061119BI", "SDK 33"),        # (Android 13) Xiaomi Redmi 10 Prime IN 
                ("Xiaomi 21061119AG", "SDK 33"),        # (Android 13) Xiaomi Redmi 10 Global 
                ("Xiaomi 2106118C", "SDK 33"),          # (Android 13) Xiaomi Mi Mix 4 5G CN 
                ("Xiaomi M2103K19I", "SDK 33"),         # (Android 13) Xiaomi Redmi Note 10T 5G IN 
                ("Xiaomi M1908C3JGG", "SDK 33"),        # (Android 13) Xiaomi Redmi Note 8 Global 
                ("Xiaomi M2104K10I", "SDK 33"),         # (Android 13) Xiaomi Poco F3 Gt 5G IN 
                ("Xiaomi M2101K9R", "SDK 33"),          # (Android 13) Xiaomi Mi 11 Lite 5G JP 
                ("Xiaomi M2103K19PI", "SDK 33"),        # (Android 13) Xiaomi Poco M3 Pro 5G IN 
                ("Xiaomi M2103K19PG", "SDK 33"),        # (Android 13) Xiaomi Poco M3 Pro 5G Global 
                ("Xiaomi M2103K19G", "SDK 33"),         # (Android 13) Xiaomi Redmi Note 10 5G Global 
                ("Xiaomi M2101K7BG", "SDK 33"),         # (Android 13) Xiaomi Redmi Note 10S Global 
                ("Xiaomi M2104K10C", "SDK 33"),         # (Android 13) Xiaomi Redmi K40 Game Enhanced 5G CN 
                ("Xiaomi M2101K9AG", "SDK 33"),         # (Android 13) Xiaomi Mi 11 Lite 4G Global 
                ("Xiaomi M2101K9C", "SDK 33"),          # (Android 13) Xiaomi Mi 11 Youth 5G CN 
                ("Xiaomi M2101K9G", "SDK 33"),          # (Android 13) Xiaomi Mi 11 Lite 5G Global 
                ("Xiaomi M2102J2SC", "SDK 33"),         # (Android 13) Xiaomi Mi 10S 5G CN 
                ("Xiaomi M2102J20SI", "SDK 33"),        # (Android 13) Xiaomi Poco X3 Pro IN 
                ("Xiaomi M2012K11AG", "SDK 33"),        # (Android 13) Xiaomi Poco F3 5G Global 
                ("Xiaomi M2102J20SG", "SDK 33"),        # (Android 13) Xiaomi Poco X3 Pro Global 
                ("Xiaomi M2002J9C", "SDK 33"),          # (Android 13) Xiaomi Mi 10 Lite Zoom 5G CN 
                ("Xiaomi M2012K11AI", "SDK 33"),        # (Android 13) Xiaomi Mi 11X 5G IN 
                ("Xiaomi M2102K1AC", "SDK 33"),         # (Android 13) Xiaomi Mi 11 Pro 5G CN 
                ("Xiaomi M2012K11G", "SDK 33"),         # (Android 13) Xiaomi Mi 11I 5G Global 
                ("Xiaomi M2102K1C", "SDK 33"),          # (Android 13) Xiaomi Mi 11 Ultra 5G CN 
                ("Xiaomi M2011K2G", "SDK 33"),          # (Android 13) Xiaomi Mi 11 5G Global 
                ("Xiaomi M2012K11I", "SDK 33"),         # (Android 13) Xiaomi Mi 11X Pro 5G IN 
                ("Xiaomi M2102K1G", "SDK 33"),          # (Android 13) Xiaomi Mi 11 Ultra 5G Global 
                ("Xiaomi M2101K6P", "SDK 33"),          # (Android 13) Xiaomi Redmi Note 10 Pro 4G IN 
                ("Xiaomi M2010J19SL", "SDK 33"),        # (Android 13) Xiaomi Redmi 9T LATAM 
                ("Xiaomi M2010J19SY", "SDK 33"),        # (Android 13) Xiaomi Redmi 9T RU 
                ("Xiaomi M2010J19SI", "SDK 33"),        # (Android 13) Xiaomi Redmi 9 Power 4G IN 
                ("Xiaomi M2101K6R", "SDK 33"),          # (Android 13) Xiaomi Redmi Note 10 Pro 4G LATAM 
                ("Xiaomi M2101K7AG", "SDK 33"),         # (Android 13) Xiaomi Redmi Note 10 4G Global 
                ("Xiaomi M2101K7AI", "SDK 33"),         # (Android 13) Xiaomi Redmi Note 10 4G IN 
                ("Xiaomi M2101K6I", "SDK 33"),          # (Android 13) Xiaomi Redmi Note 10 Pro Max 4G IN 
                ("Xiaomi M2101K6G", "SDK 33"),          # (Android 13) Xiaomi Redmi Note 10 Pro 4G Global 
                ("Xiaomi M2012K11AC", "SDK 33"),        # (Android 13) Xiaomi Redmi K40 5G CN 
                ("Xiaomi M2012K11C", "SDK 33"),         # (Android 13) Xiaomi Redmi K40 Pro 5G CN 
                ("Xiaomi M2012K11Q", "SDK 33"),         # (Android 13) Xiaomi Redmi K40 Pro+ 5G CN 
                ("Xiaomi M2010J19CI", "SDK 33"),        # (Android 13) Xiaomi Poco M3 IN 
                ("Xiaomi M2010J19SR", "SDK 33"),        # (Android 13) Xiaomi Redmi 9T JP 
                ("Xiaomi M2007J22R", "SDK 33"),         # (Android 13) Xiaomi Redmi Note 9T 5G JP 
                ("Xiaomi M2002J9G", "SDK 33"),          # (Android 13) Xiaomi Mi 10 Lite 5G Global 
                ("Xiaomi M2010J19SG", "SDK 33"),        # (Android 13) Xiaomi Redmi 9T Global 
                ("Xiaomi M2007J22G", "SDK 33"),         # (Android 13) Xiaomi Redmi Note 9T 5G Global 
                ("Xiaomi M2004J19I", "SDK 33"),         # (Android 13) Xiaomi Redmi 9 Prime IN 
                ("Xiaomi M2003J6A1I", "SDK 33"),        # (Android 13) Xiaomi Redmi Note 9 Pro IN 
                ("Xiaomi M2001J2I", "SDK 33"),          # (Android 13) Xiaomi Mi 10 5G IN 
                ("Xiaomi M2007J3SI", "SDK 33"),         # (Android 13) Xiaomi Mi 10T Pro 5G IN 
                ("Xiaomi M2007J3SP", "SDK 33"),         # (Android 13) Xiaomi Mi 10T 5G IN 
                ("Xiaomi M2010J19CT", "SDK 33"),        # (Android 13) Xiaomi Redmi Note 9 4G CN 
                ("Xiaomi M2007J22C", "SDK 33"),         # (Android 13) Xiaomi Redmi Note 9 5G CN 
                ("Xiaomi M2007J17I", "SDK 33"),         # (Android 13) Xiaomi Mi 10I 5G IN 
                ("Xiaomi M2011K2C", "SDK 33"),          # (Android 13) Xiaomi Mi 11 5G CN 
                ("Xiaomi M2007J17C", "SDK 33"),         # (Android 13) Xiaomi Redmi Note 9 Pro 5G CN 
                ("Xiaomi M2007J20CI", "SDK 33"),        # (Android 13) Xiaomi Poco X3 IN 
                ("Xiaomi M2007J20CG", "SDK 33"),        # (Android 13) Xiaomi Poco X3 Nfc Global 
                ("Xiaomi M2010J19CG", "SDK 33"),        # (Android 13) Xiaomi Poco M3 Global 
                ("Xiaomi M2007J3SC", "SDK 33"),         # (Android 13) Xiaomi Redmi K30S 5G CN 
                ("Xiaomi M2006C3LVG", "SDK 33"),        # (Android 13) Xiaomi Redmi 9At Global 
                ("Xiaomi M2006C3MNG", "SDK 33"),        # (Android 13) Xiaomi Redmi 9C Nfc Global 
                ("Xiaomi M2006C3MI", "SDK 33"),         # (Android 13) Xiaomi Pocophone Poco C3 IN 
                ("Xiaomi M2006C3MG", "SDK 33"),         # (Android 13) Xiaomi Redmi 9C Global 
                ("Xiaomi M2007J3SY", "SDK 33"),         # (Android 13) Xiaomi Mi 10T 5G Global 
                ("Xiaomi M2007J17G", "SDK 33"),         # (Android 13) Xiaomi Mi 10T Lite 5G Global 
                ("Xiaomi M2007J3SG", "SDK 33"),         # (Android 13) Xiaomi Mi 10T Pro 5G Global 
                ("Xiaomi M2006J10C", "SDK 33"),         # (Android 13) Xiaomi Redmi K30 Ultra 5G CN 
                ("Xiaomi M2007J1SC", "SDK 33"),         # (Android 13) Xiaomi Mi 10 Ultra CN 
                ("Xiaomi M2003J6CI", "SDK 33"),         # (Android 13) Xiaomi Pocophone Poco M2 Pro IN 
                ("Xiaomi M2002J9S", "SDK 33"),          # (Android 13) Xiaomi Mi 10 Lite 5G KR 
                ("Xiaomi M2006C3LC", "SDK 33"),         # (Android 13) Xiaomi Redmi 9A CN 
                ("Xiaomi M2006C3LG", "SDK 33"),         # (Android 13) Xiaomi Redmi 9A Global 
                ("Xiaomi M2004J19C", "SDK 33"),         # (Android 13) Xiaomi Redmi 9 CN 
                ("Xiaomi M2002J9R", "SDK 33"),          # (Android 13) Xiaomi Mi 10 Lite 5G Xig01 JP 
                ("Xiaomi M2004J19G", "SDK 33"),         # (Android 13) Xiaomi Redmi 9 Global 
                ("Xiaomi M2004J7AC", "SDK 33"),         # (Android 13) Xiaomi Redmi 10X 5G CN 
                ("Xiaomi M2004J7BC", "SDK 33"),         # (Android 13) Xiaomi Redmi 10X Pro 5G CN 
                ("Xiaomi M2003J6B2G", "SDK 33"),        # (Android 13) Xiaomi Redmi Note 9 Pro Global 
                ("Xiaomi M2003J15SC", "SDK 33"),        # (Android 13) Xiaomi Redmi 10X 4G CN 
                ("Xiaomi M2003J15SS", "SDK 33"),        # (Android 13) Xiaomi Redmi Note 9 Global 
                ("Xiaomi M2003J15SG", "SDK 33"),        # (Android 13) Xiaomi Redmi Note 9 Global 
                ("Xiaomi M2002F4LG", "SDK 33"),         # (Android 13) Xiaomi Mi Note 10 Lite Global 
                ("Xiaomi M2002J9E", "SDK 33"),          # (Android 13) Xiaomi Mi 10 Youth 5G CN 
                ("Xiaomi M2004J11G", "SDK 33"),         # (Android 13) Xiaomi Pocophone Poco F2 Pro 5G Global 
                ("Xiaomi M2001G7AE", "SDK 33"),         # (Android 13) Xiaomi Redmi K30 5G CN 
                ("Xiaomi M2001J11E", "SDK 33"),         # (Android 13) Xiaomi Redmi K30 Pro Zoom 5G CN 
                ("Xiaomi M2001J2E", "SDK 33"),          # (Android 13) Xiaomi Mi 10 5G CN 
                ("Xiaomi M2003J6B1I", "SDK 33"),        # (Android 13) Xiaomi Redmi Note 9 Pro Max IN 
                ("Xiaomi M2001J2G", "SDK 33"),          # (Android 13) Xiaomi Mi 10 5G Global 
                ("Xiaomi M2003J6A1G", "SDK 33"),        # (Android 13) Xiaomi Redmi Note 9S Global 
                ("Xiaomi M2001J1G", "SDK 33"),          # (Android 13) Xiaomi Mi 10 Pro 5G Global 
                ("Xiaomi M2001J1E", "SDK 33"),          # (Android 13) Xiaomi Mi 10 Pro 5G CN 
                ("Xiaomi M1906G7I", "SDK 31"),          # (Android 12) Xiaomi Redmi Note 8 Pro IN 
                ("Xiaomi M2001C3K3I", "SDK 31"),        # (Android 12) Xiaomi Redmi 8A Dual IN 
                ("Xiaomi M1912G7BI", "SDK 33"),         # (Android 13) Xiaomi Pocophone Poco X2 IN 
                ("Xiaomi M1912G7BE", "SDK 33"),         # (Android 13) Xiaomi Redmi K30 CN 
                ("Xiaomi M1908F1XE", "SDK 31"),         # (Android 12) Xiaomi Mi 9 Pro 5G CN 
                ("Xiaomi M1810E5GG", "SDK 31"),         # (Android 12) Xiaomi Mi Mix 3 5G Global 
                ("Xiaomi M1910F4S", "SDK 31"),          # (Android 12) Xiaomi Mi Note 10 Pro Global 
                ("Xiaomi M1910F4E", "SDK 31"),          # (Android 12) Xiaomi Mi Cc9 Pro CN 
                ("Xiaomi M1908C3XG", "SDK 31"),         # (Android 12) Xiaomi Redmi Note 8T Global 
                ("Xiaomi M1910F4G", "SDK 31"),          # (Android 12) Xiaomi Mi Note 10 Global 
                ("Xiaomi M1908C3IE", "SDK 31"),         # (Android 12) Xiaomi Redmi 8 CN 
                ("Xiaomi M1908C3KE", "SDK 31"),         # (Android 12) Xiaomi Redmi 8A CN 
                ("Xiaomi M1908C3IH", "SDK 31"),         # (Android 12) Xiaomi Redmi 8 
                ("Xiaomi M1908C3IG", "SDK 31"),         # (Android 12) Xiaomi Redmi 8 Global 
                ("Xiaomi M1908C3KI", "SDK 31"),         # (Android 12) Xiaomi Redmi 8A IN 
                ("Xiaomi M1908C3KG", "SDK 31"),         # (Android 12) Xiaomi Redmi 8A Global 
                ("Xiaomi M1906G7G", "SDK 31"),          # (Android 12) Xiaomi Redmi Note 8 Pro Global 
                ("Xiaomi M1904F3BG", "SDK 31"),         # (Android 12) Xiaomi Mi 9 Lite Global 
                ("Xiaomi M1903F11A", "SDK 31"),         # (Android 12) Xiaomi Redmi K20 Pro Prime CN 
                ("Xiaomi M1903F11G", "SDK 31"),         # (Android 12) Xiaomi Mi 9T Pro Global 
                ("Xiaomi M1908C3JH", "SDK 31"),         # (Android 12) Xiaomi Redmi Note 8 
                ("Xiaomi M1908C3JG", "SDK 31"),         # (Android 12) Xiaomi Redmi Note 8 Global 
                ("Xiaomi M1906G7T", "SDK 31"),          # (Android 12) Xiaomi Redmi Note 8 Pro CN 
                ("Xiaomi M1906G7E", "SDK 31"),          # (Android 12) Xiaomi Redmi Note 8 Pro CN 
                ("Xiaomi M1908C3JE", "SDK 31"),         # (Android 12) Xiaomi Redmi Note 8 CN 
                ("Xiaomi M1906F9SI", "SDK 31"),         # (Android 12) Xiaomi Mi A3 IN 
                ("Xiaomi M1902F1A", "SDK 31"),          # (Android 12) Xiaomi Mi 9 CN 
                ("Xiaomi M1902F1G", "SDK 31"),          # (Android 12) Xiaomi Mi 9 Global 
                ("Xiaomi M1903F10G", "SDK 31"),         # (Android 12) Xiaomi Mi 9T Global 
                ("Xiaomi M1906F9SH", "SDK 31"),         # (Android 12) Xiaomi Mi A3 Global 
                ("Xiaomi M1906F9SC", "SDK 31"),         # (Android 12) Xiaomi Mi Cc9E CN 
                ("Xiaomi M1904F3BC", "SDK 31"),         # (Android 12) Xiaomi Mi Cc9 CN 
                ("Xiaomi M1904F3BT", "SDK 31"),         # (Android 12) Xiaomi Mi Cc9 CN 
                ("Xiaomi M1903C3EI", "SDK 31"),         # (Android 12) Xiaomi Redmi 7A IN 
                ("Xiaomi M1903C3EH", "SDK 31"),         # (Android 12) Xiaomi Redmi 7A 
                ("Xiaomi M1903C3EG", "SDK 31"),         # (Android 12) Xiaomi Redmi 7A Global 
                ("Xiaomi M1903F11T", "SDK 31"),         # (Android 12) Xiaomi Redmi K20 Pro CN 
                ("Xiaomi M1903F10T", "SDK 31"),         # (Android 12) Xiaomi Redmi K20 CN 
                ("Xiaomi M1903C3EE", "SDK 31"),         # (Android 12) Xiaomi Redmi 7A CN 
                ("Xiaomi M1903F10A", "SDK 31"),         # (Android 12) Xiaomi Redmi K20 CN 
                ("Xiaomi M1903C3ET", "SDK 31"),         # (Android 12) Xiaomi Redmi 7A CN 
                ("Xiaomi M1901F7I", "SDK 31"),          # (Android 12) Xiaomi Redmi Note 7 Th 
                ("Xiaomi M1810F6G", "SDK 31"),          # (Android 12) Xiaomi Redmi Y3 Global 
                ("Xiaomi M1901F7H", "SDK 31"),          # (Android 12) Xiaomi Redmi Note 7 LATAM 
                ("Xiaomi M1810F6LH", "SDK 31"),         # (Android 12) Xiaomi Redmi 7 
                ("Xiaomi M1810F6LI", "SDK 31"),         # (Android 12) Xiaomi Redmi 7 IN 
                ("Xiaomi M1810F6I", "SDK 31"),          # (Android 12) Xiaomi Redmi Y3 IN 
                ("Xiaomi M1903F2G", "SDK 31"),          # (Android 12) Xiaomi Mi 9 Se Global 
                ("Xiaomi M1810F6LG", "SDK 31"),         # (Android 12) Xiaomi Redmi 7 Global 
                ("Xiaomi M1810F6LE", "SDK 31"),         # (Android 12) Xiaomi Redmi 7 CN 
                ("Xiaomi M1901F7G", "SDK 31"),          # (Android 12) Xiaomi Redmi Note 7 Global 
                ("Xiaomi M1901F7BE", "SDK 31"),         # (Android 12) Xiaomi Redmi Note 7 Pro CN 
                ("Xiaomi M1901F7S", "SDK 31"),          # (Android 12) Xiaomi Redmi Note 7 Pro IN 
                ("Xiaomi M1903F2A", "SDK 31"),          # (Android 12) Xiaomi Mi 9 Se CN 
                ("Xiaomi M1902F1T", "SDK 31"),          # (Android 12) Xiaomi Mi 9 CN 
                ("Xiaomi M1901F7E", "SDK 31"),          # (Android 12) Xiaomi Redmi Note 7 CN 
                ("Xiaomi M1804D2ST", "SDK 29"),         # (Android 10) Xiaomi Mi 6X CN 
                ("Xiaomi M1804D2SE", "SDK 29"),         # (Android 10) Xiaomi Mi 6X CN 
                ("Xiaomi M1803D5XA", "SDK 29"),         # (Android 10) Xiaomi Mi Mix 2S Global 
                ("Xiaomi M1803D5XT", "SDK 29"),         # (Android 10) Xiaomi Mi Mix 2S CN 
                ("Xiaomi M1803D5XE", "SDK 29"),         # (Android 10) Xiaomi Mi Mix 2S CN 
                ]





    deviceList: List[DeviceInfo] = []

    @classmethod
    def __gen__(cls: Type[AndroidDevice]) -> None:

        if len(cls.deviceList) == 0:

            results: List[DeviceInfo] = []

            for device in cls.device_models:
                results.append(DeviceInfo(*device))

            cls.deviceList = results


class iOSDeivce(SystemInfo):

    device_models = {
        5: ["S"],
        6: [" Plus", "", "S", "S Plus"],
        7: ["", " Plus"],
        8: ["", " Plus"],
        10: ["", "S", "S Max", "R"],
        11: ["", " Pro", " Pro Max"],
        12: [" mini", "", " Pro", " Pro Max"],
        13: [" Pro", " Pro Max", " Mini", ""],
    }

    system_versions: Dict[int, Dict[int, List[int]]] = {
        15: {2: [], 1: [1], 0: [2, 1]},
        14: {8: [1], 7: [1], 6: [], 5: [1], 4: [2, 1], 3: [], 2: [1], 1: [], 0: [1]},
        13: {7: [], 6: [1], 5: [1], 4: [1], 3: [1], 2: [3, 2], 1: [3, 2, 1]},
        12: {
            5: [5, 4, 3, 2, 1],
            4: [9, 8, 7, 6, 5, 4, 3, 2, 1],
            3: [2, 1],
            11: [0],
            2: [],
            1: [4, 3, 2, 1],
            0: [1],
        },
    }

    deviceList: List[DeviceInfo] = []

    @classmethod
    def __gen__(cls: Type[iOSDeivce]) -> None:

        if len(cls.deviceList) == 0:
            results: List[DeviceInfo] = []

            # ! SHITTY CODE BECAUSE I HAD TO CHECK FOR THE RIGHT VERSION
            for id_model in cls.device_models:
                if id_model == 13:
                    available_versions = [15]
                elif id_model == 12:
                    available_versions = [14, 15]
                elif id_model == 11:
                    available_versions = [13, 14, 15]
                elif id_model == 5:
                    available_versions = [12]
                else:
                    available_versions = [12, 13, 14, 15]

                for model_name in cls.device_models[id_model]:

                    if id_model == 10:
                        id_model = "X"
                    device_model = f"iPhone {id_model}{model_name}"

                    for major in available_versions:
                        for minor, patches in cls.system_versions[major].items():

                            if len(patches) == 0:
                                results.append(
                                    DeviceInfo(device_model, f"{major}.{minor}")
                                )
                            else:
                                for patch in patches:
                                    results.append(
                                        DeviceInfo(
                                            device_model, f"{major}.{minor}.{patch}"
                                        )
                                    )

            cls.deviceList = results
