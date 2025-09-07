"""
Panchanga calculation library.

Provides a PanchangaEngine class that can be reused by any UI or script.
"""
from __future__ import annotations
import datetime as dt
from dataclasses import dataclass
from zoneinfo import ZoneInfo
import swisseph as swe
from typing import Optional
from enum import Enum
import functools

# ─────────────────────────────────────────────────────────────────────────────
# ENUMS
# ─────────────────────────────────────────────────────────────────────────────

class PanchangaConstants(Enum):
    """Enumerations for Panchanga elements."""
    EN_TITHI_15 = ["Pratipada", "Dvitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima"]
    TE_TITHI_15 = ["పాడ్యమి", "విదియ", "తదియ", "చవితి", "పంచమి", "షష్ఠి", "సప్తమి", "అష్టమి", "నవమి", "దశమి", "ఏకాదశి", "ద్వాదశి", "త్రయోదశి", "చతుర్దశి", "పౌర్ణమి"]
    
    EN_NAKSHATRAS = ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"]
    TE_NAKSHATRAS = ["అశ్విని", "భరణి", "కృత్తిక", "రోహిణి", "మృగశిర", "ఆరుద్ర", "పునర్వసు", "పుష్యమి", "ఆశ్లేష", "మఖ", "పుబ్బ", "ఉత్తర", "హస్త", "చిత్త", "స్వాతి", "విశాఖ", "అనూరాధ", "జ్యేష్ఠ", "మూల", "పూర్వాషాఢ", "ఉత్తరాషాఢ", "శ్రవణం", "ధనిష్ఠ", "శతభిష", "పూర్వాభాద్ర", "ఉత్తరాభాద్ర", "రేవతి"]

    EN_YOGAS = ["Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda", "Sukarma", "Dhriti", "Shula", "Ganda", "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra", "Siddhi", "Vyatipata", "Variyana", "Parigha", "Shiva", "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma", "Indra", "Vaidhriti"]
    TE_YOGAS = ["విష్కంభం", "ప్రీతి", "ఆయుష్మాన్", "సౌభాగ్య", "శోభన", "అతిగండ", "సుకర్మ", "ధృతి", "శూల", "గండ", "వృద్ధి", "ధ్రువ", "వ్యాఘాత", "హర్షణ", "వజ్ర", "సిద్ధి", "వ్యతీపాత", "వరీయాన", "పరిఘ", "శివ", "సిద్ధ", "సాధ్య", "శుభ", "శుక్ల", "బ్రహ్మ", "ఇంద్ర", "వైధృతి"]
    
    EN_KARANAS = ["Bava", "Balava", "Kaulava", "Taitila", "Garaja", "Vanija", "Vishti", "Shakuni", "Chatushpada", "Naga", "Kinstughna"]
    TE_KARANAS = ["బవ", "బాలవ", "కౌలవ", "తైతిల", "గరజ", "వణిజ", "విష్టి", "శకున", "చతుష్పాద", "నాగ", "కింస్తుఘ్న"]
    
    EN_WEEKDAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    TE_WEEKDAYS = ["ఆదివారం", "సోమవారం", "మంగళవారం", "బుధవారం", "గురువారం", "శుక్రవారం", "శనివారం"]

    EN_MASAS = ["Chaitra", "Vaishakha", "Jyeshtha", "Ashadha", "Shravana", "Bhadrapada", "Ashwin", "Kartika", "Margashirsha", "Pausha", "Magha", "Phalguna"]
    TE_MASAS = ["చైత్రం", "వైశాఖం", "జ్యేష్టం", "ఆషాఢం", "శ్రావణం", "భాద్రపదం", "ఆశ్వీయుజం", "కార్తీకం", "మార్గశిరం", "పుష్యం", "మాఘం", "ఫాల్గుణం"]
    
    EN_RASHIS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    TE_RASHIS = ["మేషం", "వృషభం", "మిథునం", "కర్కాటకం", "సింహం", "కన్య", "తుల", "వృశ్చికం", "ధనస్సు", "మకరం", "కుంభం", "మీనం"]
    
# ─────────────────────────────────────────────────────────────────────────────
# DATACLASSEES
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class PanchangaInfo:
    """A dataclass to hold all panchanga details."""
    datetime: dt.datetime
    tithi_en: str
    tithi_te: str
    tithi_idx: int
    tithi_end_time: Optional[dt.datetime]
    nakshatra_en: str
    nakshatra_te: str
    nakshatra_idx: int
    nakshatra_end_time: Optional[dt.datetime]
    yoga_en: str
    yoga_te: str
    yoga_idx: int
    yoga_end_time: Optional[dt.datetime]
    karana_en: str
    karana_te: str
    karana_idx: int
    karana_end_time: Optional[dt.datetime]
    weekday_en: str
    weekday_te: str

@dataclass
class MasaInfo:
    """A dataclass to hold details about the Hindu lunar month."""
    masa_en: str
    masa_te: str
    masa_idx: int
    adhika_masa: bool

# ─────────────────────────────────────────────────────────────────────────────
# PANCHANGA ENGINE
# ─────────────────────────────────────────────────────────────────────────────

class PanchangaEngine:
    """
    A class to calculate panchanga details for a given location and timezone.
    
    The calculations are based on the Swiss Ephemeris library.
    """
    def __init__(self, lat: float, lon: float, timezone: str, masa_system: str = "amanta"):
        """
        Initializes the PanchangaEngine with location and timezone.
        
        Args:
            lat (float): Latitude of the location.
            lon (float): Longitude of the location.
            timezone (str): Timezone string (e.g., "Asia/Kolkata").
            masa_system (str): The masa system to use ("amanta" or "purnimanta").
        """
        self.lat = lat
        self.lon = lon
        self.tz = ZoneInfo(timezone)
        self.masa_system = masa_system
        self._cache = {}
        
    def _sid_lon(self, jd_ut: float, body: int) -> float:
        """
        Calculates the tropical longitude of a celestial body and converts it to sidereal.
        
        Args:
            jd_ut (float): Julian day in UTC.
            body (int): The Swiss Ephemeris body ID.
            
        Returns:
            float: The sidereal longitude in degrees.
        """
        swe.set_ephe_path("/usr/share/ephe")
        res_trop = swe.calc_ut(jd_ut, body)
        sidereal = swe.get_ayanamsa_ut(jd_ut)
        
        lon = res_trop[0][0] - sidereal
        return lon % 360
    
    def _find_next_crossing_deg(self, jd_ut: float, lon_func, target_deg: float) -> Optional[dt.datetime]:
        """
        Finds the next Julian Day when a celestial body crosses a specific longitude.
        
        Args:
            jd_ut (float): Starting Julian day in UTC.
            lon_func (callable): A function that takes a Julian day and returns a longitude.
            target_deg (float): The target longitude to find.
            
        Returns:
            Optional[dt.datetime]: The datetime of the crossing, or None if not found.
        """
        res = swe.solve_transit_ut(jd_ut, swe.MOON, swe.DEG, target_deg)
        if res and res[0][0] > jd_ut:
            # Convert Julian Day to UTC datetime and then to local timezone
            utc_datetime = swe.julday_to_utc(res[0][0])
            return dt.datetime(utc_datetime[0], utc_datetime[1], utc_datetime[2], 
                               utc_datetime[3], utc_datetime[4], int(utc_datetime[5]), 
                               tzinfo=dt.timezone.utc)
        return None
    
    def _get_base(self) -> dict:
        """
        Gets the base Julian day and other fundamental properties.
        
        Returns:
            dict: A dictionary with base calculation values.
        """
        now_local = dt.datetime.now(self.tz)
        now_utc = now_local.astimezone(dt.timezone.utc)
        
        jd_ut = swe.utc_to_julday(now_utc.year, now_utc.month, now_utc.day, now_utc.hour, now_utc.minute, now_utc.second)[1]
        
        sun_lon = self._sid_lon(jd_ut, swe.SUN)
        moon_lon = self._sid_lon(jd_ut, swe.MOON)
        
        return {
            'now_local': now_local,
            'now_utc': now_utc,
            'jd_ut': jd_ut,
            'sun_lon': sun_lon,
            'moon_lon': moon_lon,
            'tz': self.tz
        }
        
    @functools.cached_property
    def _cached_base(self):
        """Cached base calculations for performance."""
        return self._get_base()

    def get_datetime(self) -> dt.datetime:
        """Returns the current local datetime."""
        return self._cached_base['now_local']
    
    def get_tithi(self) -> tuple[str, str, int, Optional[dt.datetime]]:
        """Calculates the current Tithi."""
        b = self._cached_base
        if 'tithi' in self._cache:
            return self._cache['tithi']
        
        tithi_lon = (b['moon_lon'] - b['sun_lon']) % 360
        tithi_idx = int(tithi_lon / 12)
        
        tithi_en = PanchangaConstants.EN_TITHI_15.value[tithi_idx % 15]
        tithi_te = PanchangaConstants.TE_TITHI_15.value[tithi_idx % 15]
        
        target_tithi = ((tithi_idx + 1) * 12) % 360
        
        def tithi_get(jd_ut):
            sun_lon = self._sid_lon(jd_ut, swe.SUN)
            moon_lon = self._sid_lon(jd_ut, swe.MOON)
            return (moon_lon - sun_lon) % 360
        
        end_utc = self._find_next_crossing_deg(b['jd_ut'], tithi_get, target_tithi)
        tithi_end_local = end_utc.astimezone(b['tz']) if end_utc else None
        
        self._cache['tithi'] = (tithi_en, tithi_te, tithi_idx, tithi_end_local)
        return self._cache['tithi']

    def get_nakshatra(self) -> tuple[str, str, int, Optional[dt.datetime]]:
        """Calculates the current Nakshatra."""
        b = self._cached_base
        if 'nakshatra' in self._cache:
            return self._cache['nakshatra']
            
        nak_idx = int(b['moon_lon'] / (360/27))
        nak_en = PanchangaConstants.EN_NAKSHATRAS.value[nak_idx]
        nak_te = PanchangaConstants.TE_NAKSHATRAS.value[nak_idx]
        
        target_nak = ((nak_idx + 1) * (360/27)) % 360
        def moon_get(jd_ut): return self._sid_lon(jd_ut, swe.MOON)
        
        end_utc = self._find_next_crossing_deg(b['jd_ut'], moon_get, target_nak)
        nak_end_local = end_utc.astimezone(b['tz']) if end_utc else None

        self._cache['nakshatra'] = (nak_en, nak_te, nak_idx, nak_end_local)
        return self._cache['nakshatra']
    
    def get_yoga(self) -> tuple[str, str, int, Optional[dt.datetime]]:
        """Calculates the current Yoga."""
        b = self._cached_base
        if 'yoga' in self._cache:
            return self._cache['yoga']
            
        yoga_lon = (b['sun_lon'] + b['moon_lon']) % 360
        yoga_idx = int(yoga_lon / (360/27))
        
        yoga_en = PanchangaConstants.EN_YOGAS.value[yoga_idx]
        yoga_te = PanchangaConstants.TE_YOGAS.value[yoga_idx]
        
        target_yoga = ((yoga_idx + 1) * (360/27)) % 360
        def yoga_get(jd_ut):
            sun_lon = self._sid_lon(jd_ut, swe.SUN)
            moon_lon = self._sid_lon(jd_ut, swe.MOON)
            return (sun_lon + moon_lon) % 360
            
        end_utc = self._find_next_crossing_deg(b['jd_ut'], yoga_get, target_yoga)
        yoga_end_local = end_utc.astimezone(b['tz']) if end_utc else None

        self._cache['yoga'] = (yoga_en, yoga_te, yoga_idx, yoga_end_local)
        return self._cache['yoga']

    def get_karana(self) -> tuple[str, str, int, Optional[dt.datetime]]:
        """Calculates the current Karana."""
        b = self._cached_base
        if 'karana' in self._cache:
            return self._cache['karana']
        
        tithi_lon = (b['moon_lon'] - b['sun_lon']) % 360
        karana_idx = int(tithi_lon / 6)
        
        if karana_idx == 0:
            karana_en = PanchangaConstants.EN_KARANAS.value[10]
            karana_te = PanchangaConstants.TE_KARANAS.value[10]
        else:
            karana_en = PanchangaConstants.EN_KARANAS.value[karana_idx % 7]
            karana_te = PanchangaConstants.TE_KARANAS.value[karana_idx % 7]

        target_karana = ((karana_idx + 1) * 6) % 360
        
        def karana_get(jd_ut):
            sun_lon = self._sid_lon(jd_ut, swe.SUN)
            moon_lon = self._sid_lon(jd_ut, swe.MOON)
            return (moon_lon - sun_lon) % 360
            
        end_utc = self._find_next_crossing_deg(b['jd_ut'], karana_get, target_karana)
        karana_end_local = end_utc.astimezone(b['tz']) if end_utc else None

        self._cache['karana'] = (karana_en, karana_te, karana_idx, karana_end_local)
        return self._cache['karana']
    
    def get_weekday(self) -> tuple[str, str, int]:
        """Calculates the current weekday."""
        b = self._cached_base
        weekday_idx = b['now_local'].weekday()
        weekday_en = PanchangaConstants.EN_WEEKDAYS.value[weekday_idx]
        weekday_te = PanchangaConstants.TE_WEEKDAYS.value[weekday_idx]
        return weekday_en, weekday_te, weekday_idx

    def get_now(self) -> PanchangaInfo:
        """
        Calculates and returns all panchanga details for the current moment.
        
        Returns:
            PanchangaInfo: An object containing all panchanga information.
        """
        now = self.get_datetime()
        tithi_en, tithi_te, tithi_idx, tithi_end = self.get_tithi()
        nak_en, nak_te, nak_idx, nak_end = self.get_nakshatra()
        yoga_en, yoga_te, yoga_idx, yoga_end = self.get_yoga()
        kar_en, kar_te, kar_idx, kar_end = self.get_karana()
        weekday_en, weekday_te, weekday_idx = self.get_weekday()
        
        return PanchangaInfo(
            datetime=now,
            tithi_en=tithi_en,
            tithi_te=tithi_te,
            tithi_idx=tithi_idx,
            tithi_end_time=tithi_end,
            nakshatra_en=nak_en,
            nakshatra_te=nak_te,
            nakshatra_idx=nak_idx,
            nakshatra_end_time=nak_end,
            yoga_en=yoga_en,
            yoga_te=yoga_te,
            yoga_idx=yoga_idx,
            yoga_end_time=yoga_end,
            karana_en=kar_en,
            karana_te=kar_te,
            karana_idx=kar_idx,
            karana_end_time=kar_end,
            weekday_en=weekday_en,
            weekday_te=weekday_te
        )

    def update(self, lat: Optional[float] = None, lon: Optional[float] = None, timezone: Optional[str] = None, masa_system: Optional[str] = None):
        """
        Updates the engine's configuration and clears the cache.
        
        Args:
            lat (float): New latitude.
            lon (float): New longitude.
            timezone (str): New timezone string.
            masa_system (str): New masa system.
        """
        if lat is not None:
            self.lat = lat
        if lon is not None:
            self.lon = lon
        if timezone is not None:
            self.tz = ZoneInfo(timezone)
        if masa_system is not None:
            self.masa_system = masa_system
            
        self._cache = {}
        # Clear the cached property as well
        if '_cached_base' in self.__dict__:
            del self.__dict__['_cached_base']