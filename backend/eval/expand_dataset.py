"""
backend/eval/expand_dataset.py
Appends CMP-016 through CMP-075 to synthetic_1076.json.
"""
import json
from pathlib import Path

eval_file = Path(__file__).resolve().parent / "synthetic_1076.json"
with open(eval_file, "r", encoding="utf-8") as f:
    existing = json.load(f)

# Keep first 15 if already populated, prune duplicates
existing_ids = {item["id"] for item in existing}

new_items = [
  {
    "id": "CMP-016",
    "text": "11000 volt ki high tension line toot kar sadak ke paani mein gir gayi hai, chingari nikal rahi hai aur current daud raha hai!",
    "complaint_text": "11000 volt ki high tension line toot kar sadak ke paani mein gir gayi hai, chingari nikal rahi hai aur current daud raha hai!",
    "dialect": "Hinglish",
    "expected_department": "uppcl",
    "expected_urgency": 5,
    "expected_hazard": True,
    "is_life_safety_hazard": True,
    "cluster_group": "LKO_LIVE_WIRE_P1"
  },
  {
    "id": "CMP-017",
    "text": "Sadak par 4 feet gehra sewer manhole bina dhakkan ke khula hai, paani bhara hone ki wajah se dikhai nahi de raha, do bache abhi girte girte bache!",
    "complaint_text": "Sadak par 4 feet gehra sewer manhole bina dhakkan ke khula hai, paani bhara hone ki wajah se dikhai nahi de raha, do bache abhi girte girte bache!",
    "dialect": "Hindi",
    "expected_department": "nagar_nigam",
    "expected_urgency": 5,
    "expected_hazard": True,
    "is_life_safety_hazard": True,
    "cluster_group": "KNP_OPEN_MANHOLE_HAZARD"
  },
  {
    "id": "CMP-018",
    "text": "Kanya Prathmik Vidyalaya ke class 3 ki chhat ka linter crack ho kar jhul gaya hai, kabhi bhi poori chhat bachon par gir sakti hai!",
    "complaint_text": "Kanya Prathmik Vidyalaya ke class 3 ki chhat ka linter crack ho kar jhul gaya hai, kabhi bhi poori chhat bachon par gir sakti hai!",
    "dialect": "Hindi",
    "expected_department": "basic_education",
    "expected_urgency": 5,
    "expected_hazard": True,
    "is_life_safety_hazard": True,
    "cluster_group": "BLY_SCHOOL_COLLAPSE_P1"
  },
  {
    "id": "CMP-019",
    "text": "Main market Chowk ke paas distribution transformer mein achanak dhamaka hua aur tez aag ki laptein nikal rahi hain, paas mein dukaanein hain turant power kaato!",
    "complaint_text": "Main market Chowk ke paas distribution transformer mein achanak dhamaka hua aur tez aag ki laptein nikal rahi hain, paas mein dukaanein hain turant power kaato!",
    "dialect": "Hindi",
    "expected_department": "uppcl",
    "expected_urgency": 5,
    "expected_hazard": True,
    "is_life_safety_hazard": True,
    "cluster_group": "VNS_TRANSFORMER_BLAST"
  },
  {
    "id": "CMP-020",
    "text": "Gaon ke peene ke supply pipeline mein chemical factory ka jahreela chemical mil gaya hai, paani peete hi 14 log behosh ho gaye aur blood vomiting kar rahe hain!",
    "complaint_text": "Gaon ke peene ke supply pipeline mein chemical factory ka jahreela chemical mil gaya hai, paani peete hi 14 log behosh ho gaye aur blood vomiting kar rahe hain!",
    "dialect": "Hindi",
    "expected_department": "jal_nigam",
    "expected_urgency": 5,
    "expected_hazard": True,
    "is_life_safety_hazard": True,
    "cluster_group": "UNN_CHEMICAL_WATER_P1"
  },
  {
    "id": "CMP-021",
    "text": "Nadi par bani purani puliya ka beech ka pillar dhas gaya hai, bridge beech se jhuk gaya hai aur heavy traffic chal raha hai, turant route divert karo collapse hone wala hai!",
    "complaint_text": "Nadi par bani purani puliya ka beech ka pillar dhas gaya hai, bridge beech se jhuk gaya hai aur heavy traffic chal raha hai, turant route divert karo collapse hone wala hai!",
    "dialect": "Hindi",
    "expected_department": "pwd",
    "expected_urgency": 5,
    "expected_hazard": True,
    "is_life_safety_hazard": True,
    "cluster_group": "GKP_BRIDGE_COLLAPSE_P1"
  },
  {
    "id": "CMP-022",
    "text": "Industrial area warehouse se toxic gas leakage ho rahi hai, aankhon mein tez jalan aur poore mohalle mein logon ka dam ghut raha hai!",
    "complaint_text": "Industrial area warehouse se toxic gas leakage ho rahi hai, aankhon mein tez jalan aur poore mohalle mein logon ka dam ghut raha hai!",
    "dialect": "Hinglish",
    "expected_department": "health",
    "expected_urgency": 5,
    "expected_hazard": True,
    "is_life_safety_hazard": True,
    "cluster_group": "GZB_GAS_LEAK_P1"
  },
  {
    "id": "CMP-023",
    "text": "Bijli ke khambhe mein poora current utar raha hai, abhi ek gay chhoo kar mar gayi hai, school ke bachon ka aana jaana hai!",
    "complaint_text": "Bijli ke khambhe mein poora current utar raha hai, abhi ek gay chhoo kar mar gayi hai, school ke bachon ka aana jaana hai!",
    "dialect": "Hindi",
    "expected_department": "uppcl",
    "expected_urgency": 5,
    "expected_hazard": True,
    "is_life_safety_hazard": True,
    "cluster_group": "ALH_POLE_ELECTROCUTION"
  },
  {
    "id": "CMP-024",
    "text": "Gram sabha ke tole mein kal raat se 22 log cholera aur severe dehydration se tadap rahe hain, gaon mein 2 bacho ki maut ho chuki hai turant medical team bhejo!",
    "complaint_text": "Gram sabha ke tole mein kal raat se 22 log cholera aur severe dehydration se tadap rahe hain, gaon mein 2 bacho ki maut ho chuki hai turant medical team bhejo!",
    "dialect": "Hindi",
    "expected_department": "health",
    "expected_urgency": 5,
    "expected_hazard": True,
    "is_life_safety_hazard": True,
    "cluster_group": "BAP_CHOLERA_OUTBREAK"
  },
  {
    "id": "CMP-025",
    "text": "Tez barish mein retaining wall highway par dhas gayi hai, mitti aur patthar girne se aadha road block ho gaya hai aur gaadiyan phas gayi hain!",
    "complaint_text": "Tez barish mein retaining wall highway par dhas gayi hai, mitti aur patthar girne se aadha road block ho gaya hai aur gaadiyan phas gayi hain!",
    "dialect": "Hindi",
    "expected_department": "pwd",
    "expected_urgency": 5,
    "expected_hazard": True,
    "is_life_safety_hazard": True,
    "cluster_group": "MIR_LANDSLIDE_WALL_P1"
  },
  {
    "id": "CMP-026",
    "text": "Mohalle ke main feeder ka cable blast hokar sadak par gir pada hai, raste mein aag lagi hui hai koi bhi gaadi nahi nikal pa rahi!",
    "complaint_text": "Mohalle ke main feeder ka cable blast hokar sadak par gir pada hai, raste mein aag lagi hui hai koi bhi gaadi nahi nikal pa rahi!",
    "dialect": "Hindi",
    "expected_department": "uppcl",
    "expected_urgency": 5,
    "expected_hazard": True,
    "is_life_safety_hazard": True,
    "cluster_group": "AGR_CABLE_FIRE_P1"
  },
  {
    "id": "CMP-027",
    "text": "1076 par complaint darj karne ke baad dabang log pistol lekar ghar mein ghus aaye aur complaint wapas lene ke liye jaan se maarne ki dhamki de rahe hain!",
    "complaint_text": "1076 par complaint darj karne ke baad dabang log pistol lekar ghar mein ghus aaye aur complaint wapas lene ke liye jaan se maarne ki dhamki de rahe hain!",
    "dialect": "Hindi",
    "expected_department": "police",
    "expected_urgency": 5,
    "expected_hazard": True,
    "is_life_safety_hazard": True,
    "cluster_group": "MEE_ARMED_INTIMIDATION"
  },
  {
    "id": "CMP-028",
    "text": "Water pipeline burst hone se road ke neeche ki saari mitti beh gayi hai aur 10 feet gehra sinkhole ban gaya hai jismein ek auto rikshaw gir gaya!",
    "complaint_text": "Water pipeline burst hone se road ke neeche ki saari mitti beh gayi hai aur 10 feet gehra sinkhole ban gaya hai jismein ek auto rikshaw gir gaya!",
    "dialect": "Hinglish",
    "expected_department": "jal_nigam",
    "expected_urgency": 5,
    "expected_hazard": True,
    "is_life_safety_hazard": True,
    "cluster_group": "KNP_SINKHOLE_BURST_P1"
  },
  {
    "id": "CMP-029",
    "text": "Panchayat bhawan ki boundary wall raste ki taraf 45 degree jhuk chuki hai aur neeche bache khelte hain, kisi bhi waqt bacho par palat jayegi!",
    "complaint_text": "Panchayat bhawan ki boundary wall raste ki taraf 45 degree jhuk chuki hai aur neeche bache khelte hain, kisi bhi waqt bacho par palat jayegi!",
    "dialect": "Hindi",
    "expected_department": "panchayati_raj",
    "expected_urgency": 5,
    "expected_hazard": True,
    "is_life_safety_hazard": True,
    "cluster_group": "STP_WALL_COLLAPSE_P1"
  },
  {
    "id": "CMP-030",
    "text": "Hospital ke delivery ward mein oxygen cylinder leakage ki aawaz aa rahi hai aur cylinder se aag pakadne ka khatra hai, turant fire team bhejo!",
    "complaint_text": "Hospital ke delivery ward mein oxygen cylinder leakage ki aawaz aa rahi hai aur cylinder se aag pakadne ka khatra hai, turant fire team bhejo!",
    "dialect": "Hindi",
    "expected_department": "health",
    "expected_urgency": 5,
    "expected_hazard": True,
    "is_life_safety_hazard": True,
    "cluster_group": "JHS_OXYGEN_LEAK_P1"
  },
  {
    "id": "CMP-031",
    "text": "Nali totally block ho gaya hai and drain water enter kar raha hai drawing room mein, bad smell unbearable hai please send safaikarmi.",
    "complaint_text": "Nali totally block ho gaya hai and drain water enter kar raha hai drawing room mein, bad smell unbearable hai please send safaikarmi.",
    "dialect": "Hinglish",
    "expected_department": "nagar_nigam",
    "expected_urgency": 3,
    "expected_hazard": False,
    "is_life_safety_hazard": False,
    "cluster_group": "NOI_DRAIN_BLOCK"
  },
  {
    "id": "CMP-032",
    "text": "Local sub station phone cut kar raha hai, hamare phase mein low voltage aa raha hai only 90 volts, appliances burn ho rahe hain.",
    "complaint_text": "Local sub station phone cut kar raha hai, hamare phase mein low voltage aa raha hai only 90 volts, appliances burn ho rahe hain.",
    "dialect": "Hinglish",
    "expected_department": "uppcl",
    "expected_urgency": 3,
    "expected_hazard": False,
    "is_life_safety_hazard": False,
    "cluster_group": "GZB_LOW_VOLTAGE"
  },
  {
    "id": "CMP-033",
    "text": "Sadak par jo new asphalt daala tha contracter ne wo one month mein hi peel off ho gaya hai aur bade potholes create ho gaye hain.",
    "complaint_text": "Sadak par jo new asphalt daala tha contracter ne wo one month mein hi peel off ho gaya hai aur bade potholes create ho gaye hain.",
    "dialect": "Hinglish",
    "expected_department": "pwd",
    "expected_urgency": 3,
    "expected_hazard": False,
    "is_life_safety_hazard": False,
    "cluster_group": "LKO_ASPHALT_PEEL"
  },
  {
    "id": "CMP-034",
    "text": "Municipal tap se muddy water supply ho raha hai, filter machine choke ho gayi hai and water drinking ke layak bilkul nahi hai.",
    "complaint_text": "Municipal tap se muddy water supply ho raha hai, filter machine choke ho gayi hai and water drinking ke layak bilkul nahi hai.",
    "dialect": "Hinglish",
    "expected_department": "jal_nigam",
    "expected_urgency": 4,
    "expected_hazard": False,
    "is_life_safety_hazard": False,
    "cluster_group": "VNS_MUDDY_TAP"
  },
  {
    "id": "CMP-035",
    "text": "Anganwadi worker pregnant women ka ration distribute nahi kar rahi hai aur bolti hai ki stock khatam ho gaya hai jabki market mein sell ho raha hai.",
    "complaint_text": "Anganwadi worker pregnant women ka ration distribute nahi kar rahi hai aur bolti hai ki stock khatam ho gaya hai jabki market mein sell ho raha hai.",
    "dialect": "Hinglish",
    "expected_department": "wcd",
    "expected_urgency": 3,
    "expected_hazard": False,
    "is_life_safety_hazard": False,
    "cluster_group": "FAZ_PUSHTAHAR_THEFT"
  },
  {
    "id": "CMP-036",
    "text": "PHC par anti rabies vaccine out of stock bata rahe hain aur private medical store se 400 rupee ki injection khareedne ke liye slip likh kar de rahe hain.",
    "complaint_text": "PHC par anti rabies vaccine out of stock bata rahe hain aur private medical store se 400 rupee ki injection khareedne ke liye slip likh kar de rahe hain.",
    "dialect": "Hinglish",
    "expected_department": "health",
    "expected_urgency": 3,
    "expected_hazard": False,
    "is_life_safety_hazard": False,
    "cluster_group": "BTI_VACCINE_OUT"
  },
  {
    "id": "CMP-037",
    "text": "Gaon ke lekhpal zameen napne ke liye illegal cash demand kar rahe hain aur bolte hain paisa nahi doge to boundary dispute resolve nahi karenge.",
    "complaint_text": "Gaon ke lekhpal zameen napne ke liye illegal cash demand kar rahe hain aur bolte hain paisa nahi doge to boundary dispute resolve nahi karenge.",
    "dialect": "Hinglish",
    "expected_department": "revenue",
    "expected_urgency": 3,
    "expected_hazard": False,
    "is_life_safety_hazard": False,
    "cluster_group": "SLT_LEKHPAL_BRIBE"
  },
  {
    "id": "CMP-038",
    "text": "Colony entrance par open garbage disposal point bana diya hai door-to-door waste collector ne, foul smell se nikalna impossible ho gaya hai.",
    "complaint_text": "Colony entrance par open garbage disposal point bana diya hai door-to-door waste collector ne, foul smell se nikalna impossible ho gaya hai.",
    "dialect": "Hinglish",
    "expected_department": "nagar_nigam",
    "expected_urgency": 3,
    "expected_hazard": False,
    "is_life_safety_hazard": False,
    "cluster_group": "AGR_ENTRANCE_DUMP"
  },
  {
    "id": "CMP-039",
    "text": "Streetlight pole par spark ho raha hai night mein continuously, short circuit ki aawaz aa rahi hai please repair karwayein.",
    "complaint_text": "Streetlight pole par spark ho raha hai night mein continuously, short circuit ki aawaz aa rahi hai please repair karwayein.",
    "dialect": "Hinglish",
    "expected_department": "uppcl",
    "expected_urgency": 3,
    "expected_hazard": False,
    "is_life_safety_hazard": False,
    "cluster_group": "MRT_POLE_SPARK"
  },
  {
    "id": "CMP-040",
    "text": "Prathmik pathshala ke toilets mein running water supply nahi hai aur door latch toota hua hai, bacho ko bahar open mein jana padta hai.",
    "complaint_text": "Prathmik pathshala ke toilets mein running water supply nahi hai aur door latch toota hua hai, bacho ko bahar open mein jana padta hai.",
    "dialect": "Hinglish",
    "expected_department": "basic_education",
    "expected_urgency": 3,
    "expected_hazard": False,
    "is_life_safety_hazard": False,
    "cluster_group": "AZM_SCHOOL_TOILET"
  },
  {
    "id": "CMP-041",
    "text": "Hamare gram sabha mein installed solar panel battery 2 weeks pehle steal ho gayi thi, raat ko total darkness rehti hai galiyon mein.",
    "complaint_text": "Hamare gram sabha mein installed solar panel battery 2 weeks pehle steal ho gayi thi, raat ko total darkness rehti hai galiyon mein.",
    "dialect": "Hinglish",
    "expected_department": "panchayati_raj",
    "expected_urgency": 2,
    "expected_hazard": False,
    "is_life_safety_hazard": False,
    "cluster_group": "BND_SOLAR_BATTERY"
  },
  {
    "id": "CMP-042",
    "text": "PWD road repair ke baad contractor ne kankad aur unlevel gravel chhod diya hai, two wheelers slip ho rahe hain everyday.",
    "complaint_text": "PWD road repair ke baad contractor ne kankad aur unlevel gravel chhod diya hai, two wheelers slip ho rahe hain everyday.",
    "dialect": "Hinglish",
    "expected_department": "pwd",
    "expected_urgency": 3,
    "expected_hazard": False,
    "is_life_safety_hazard": False,
    "cluster_group": "JNP_GRAVEL_SLIP"
  },
  {
    "id": "CMP-043",
    "text": "Gram pradhan ne government handpump par personal immersion pump laga kar private use kar liya hai, public access restricted hai.",
    "complaint_text": "Gram pradhan ne government handpump par personal immersion pump laga kar private use kar liya hai, public access restricted hai.",
    "dialect": "Hinglish",
    "expected_department": "jal_nigam",
    "expected_urgency": 3,
    "expected_hazard": False,
    "is_life_safety_hazard": False,
    "cluster_group": "DEO_HANDPUMP_HIJACK"
  },
  {
    "id": "CMP-044",
    "text": "Mohalle ke park mein boundary wall tooti hui hai and stray cows and dogs enter karte hain, children cannot play safely.",
    "complaint_text": "Mohalle ke park mein boundary wall tooti hui hai and stray cows and dogs enter karte hain, children cannot play safely.",
    "dialect": "Hinglish",
    "expected_department": "nagar_nigam",
    "expected_urgency": 2,
    "expected_hazard": False,
    "is_life_safety_hazard": False,
    "cluster_group": "KNP_PARK_WALL"
  },
  {
    "id": "CMP-045",
    "text": "Electricity bill meter reading 4 times inflated aayi hai, online complaint portal par update nahi ho raha meter check karwayein.",
    "complaint_text": "Electricity bill meter reading 4 times inflated aayi hai, online complaint portal par update nahi ho raha meter check karwayein.",
    "dialect": "Hinglish",
    "expected_department": "uppcl",
    "expected_urgency": 2,
    "expected_hazard": False,
    "is_life_safety_hazard": False,
    "cluster_group": "LKO_METER_INFLATION"
  },
  {
    "id": "CMP-046",
    "text": "Aandhi ke chalte bada ped gir gaya jisse main road block ho gayi hai aur 11kv high tension line toot kar raste par jhul rahi hai, current daud raha hai!",
    "complaint_text": "Aandhi ke chalte bada ped gir gaya jisse main road block ho gayi hai aur 11kv high tension line toot kar raste par jhul rahi hai, current daud raha hai!",
    "dialect": "Hindi",
    "expected_department": "uppcl",
    "expected_urgency": 5,
    "expected_hazard": True,
    "is_life_safety_hazard": True,
    "cluster_group": "RAE_TREE_WIRE_P1"
  },
  {
    "id": "CMP-047",
    "text": "Jal Nigam ki underground water pipe phatne se lakhon litre paani nikal kar PWD ki taaza bani bituminous road ko dhasakar 5 feet gaddha bana diya hai.",
    "complaint_text": "Jal Nigam ki underground water pipe phatne se lakhon litre paani nikal kar PWD ki taaza bani bituminous road ko dhasakar 5 feet gaddha bana diya hai.",
    "dialect": "Hindi",
    "expected_department": "jal_nigam",
    "expected_urgency": 4,
    "expected_hazard": False,
    "is_life_safety_hazard": False,
    "cluster_group": "LKO_PIPE_ROAD_BURST"
  },
  {
    "id": "CMP-048",
    "text": "Sarkari school ke boundary ke andar kuch log hathiyar lekar ghus aaye aur school ground par zabardasti kabza karke bacho ko bahar bhaga diya.",
    "complaint_text": "Sarkari school ke boundary ke andar kuch log hathiyar lekar ghus aaye aur school ground par zabardasti kabza karke bacho ko bahar bhaga diya.",
    "dialect": "Hindi",
    "expected_department": "police",
    "expected_urgency": 5,
    "expected_hazard": True,
    "is_life_safety_hazard": True,
    "cluster_group": "STP_SCHOOL_ENCROACH_P1"
  },
  {
    "id": "CMP-049",
    "text": "Main highway ke side ki PWD nali par market walo ne solid waste kachra phek kar block kar diya hai jisse barish ka ganda paani highway par ubal raha hai.",
    "complaint_text": "Main highway ke side ki PWD nali par market walo ne solid waste kachra phek kar block kar diya hai jisse barish ka ganda paani highway par ubal raha hai.",
    "dialect": "Hindi",
    "expected_department": "nagar_nigam",
    "expected_urgency": 3,
    "expected_hazard": False,
    "is_life_safety_hazard": False,
    "cluster_group": "BTH_HIGHWAY_DRAIN"
  },
  {
    "id": "CMP-050",
    "text": "Primary school mein mid day meal khakar 35 bache severely sick ho gaye hain aur unhe vomiting hone lagi hai, turant ambulance aur doctors bhejo!",
    "complaint_text": "Primary school mein mid day meal khakar 35 bache severely sick ho gaye hain aur unhe vomiting hone lagi hai, turant ambulance aur doctors bhejo!",
    "dialect": "Hindi",
    "expected_department": "health",
    "expected_urgency": 5,
    "expected_hazard": True,
    "is_life_safety_hazard": True,
    "cluster_group": "FTH_FOOD_POISON_P1"
  },
  {
    "id": "CMP-051",
    "text": "Nagar Nigam ki sewer line leak hokar Jal Nigam ki peene ke paani ki supply line mein ghus gayi hai, gharon mein sewage ka paani supply ho raha hai log bimar pad rahe hain.",
    "complaint_text": "Nagar Nigam ki sewer line leak hokar Jal Nigam ki peene ke paani ki supply line mein ghus gayi hai, gharon mein sewage ka paani supply ho raha hai log bimar pad rahe hain.",
    "dialect": "Hindi",
    "expected_department": "jal_nigam",
    "expected_urgency": 5,
    "expected_hazard": True,
    "is_life_safety_hazard": True,
    "cluster_group": "KNP_SEWER_INTO_DRINKING"
  },
  {
    "id": "CMP-052",
    "text": "School ki chhat ke theek upar se UPPCL ka 440 volt nanga wire guzar raha hai jise bachhe hath se chhoo sakte hain, kisi din bache ki jaan chali jayegi.",
    "complaint_text": "School ki chhat ke theek upar se UPPCL ka 440 volt nanga wire guzar raha hai jise bachhe hath se chhoo sakte hain, kisi din bache ki jaan chali jayegi.",
    "dialect": "Hindi",
    "expected_department": "uppcl",
    "expected_urgency": 5,
    "expected_hazard": True,
    "is_life_safety_hazard": True,
    "cluster_group": "HRD_ROOF_OVERHEAD_WIRE"
  },
  {
    "id": "CMP-053",
    "text": "Gaon ki link road par bani PWD puliya tooti hui hai jiski wajah se gaon ka poora nali ka paani khet mein bhar raha hai aur fasal doob gayi hai.",
    "complaint_text": "Gaon ki link road par bani PWD puliya tooti hui hai jiski wajah se gaon ka poora nali ka paani khet mein bhar raha hai aur fasal doob gayi hai.",
    "dialect": "Hindi",
    "expected_department": "pwd",
    "expected_urgency": 4,
    "expected_hazard": False,
    "is_life_safety_hazard": False,
    "cluster_group": "BLY_BROKEN_CULVERT_CROP"
  },
  {
    "id": "CMP-054",
    "text": "Market road par illegal thela walo ne footpath par kabza kar rakha hai aur hatane ko bolo to chaku nikal kar marne pe utaru ho jaate hain.",
    "complaint_text": "Market road par illegal thela walo ne footpath par kabza kar rakha hai aur hatane ko bolo to chaku nikal kar marne pe utaru ho jaate hain.",
    "dialect": "Hindi",
    "expected_department": "police",
    "expected_urgency": 4,
    "expected_hazard": True,
    "is_life_safety_hazard": True,
    "cluster_group": "LKO_FOOTPATH_THREAT"
  },
  {
    "id": "CMP-055",
    "text": "Anganwadi center ki kacchi deewar barish se dhas gayi hai aur pushtahar ka sara ration mitti mein dab gaya hai, karyakarti center nahi khol rahi.",
    "complaint_text": "Anganwadi center ki kacchi deewar barish se dhas gayi hai aur pushtahar ka sara ration mitti mein dab gaya hai, karyakarti center nahi khol rahi.",
    "dialect": "Hindi",
    "expected_department": "wcd",
    "expected_urgency": 3,
    "expected_hazard": False,
    "is_life_safety_hazard": False,
    "cluster_group": "GKP_ANGANWADI_WALL"
  },
  {
    "id": "CMP-056",
    "text": "District hospital ke gate ke samne aawara saand aur kutto ka aatank hai, emergency ambulance aane par rasta block kar dete hain aur do logon ko patak diya hai.",
    "complaint_text": "District hospital ke gate ke samne aawara saand aur kutto ka aatank hai, emergency ambulance aane par rasta block kar dete hain aur do logon ko patak diya hai.",
    "dialect": "Hindi",
    "expected_department": "nagar_nigam",
    "expected_urgency": 4,
    "expected_hazard": False,
    "is_life_safety_hazard": False,
    "cluster_group": "VNS_HOSPITAL_STRAY_CATTLE"
  },
  {
    "id": "CMP-057",
    "text": "Gram panchayat ki open drainage line choke hone se ganda keechad parishadiya primary school ke playground mein 2 feet tak bhar gaya hai.",
    "complaint_text": "Gram panchayat ki open drainage line choke hone se ganda keechad parishadiya primary school ke playground mein 2 feet tak bhar gaya hai.",
    "dialect": "Hindi",
    "expected_department": "panchayati_raj",
    "expected_urgency": 3,
    "expected_hazard": False,
    "is_life_safety_hazard": False,
    "cluster_group": "JNP_SCHOOL_DRAIN_FLOOD"
  },
  {
    "id": "CMP-058",
    "text": "Thank you so much Nagar Nigam for turning our street into a personal swimming pool for the 5th day, should we buy boats now?",
    "complaint_text": "Thank you so much Nagar Nigam for turning our street into a personal swimming pool for the 5th day, should we buy boats now?",
    "dialect": "English",
    "expected_department": "nagar_nigam",
    "expected_urgency": 3,
    "expected_hazard": False,
    "is_life_safety_hazard": False,
    "cluster_group": "LKO_SARCASTIC_WATERLOG"
  },
  {
    "id": "CMP-059",
    "text": "Kya hum electricity bill mombatti jalane ke shauk mein bharte hain? Chautha din hai jab pura mohalla andhere mein aadhi raat kaat raha hai!",
    "complaint_text": "Kya hum electricity bill mombatti jalane ke shauk mein bharte hain? Chautha din hai jab pura mohalla andhere mein aadhi raat kaat raha hai!",
    "dialect": "Hinglish",
    "expected_department": "uppcl",
    "expected_urgency": 4,
    "expected_hazard": False,
    "is_life_safety_hazard": False,
    "cluster_group": "VNS_ANGRY_BLACKOUT"
  },
  {
    "id": "CMP-060",
    "text": "Master ji school ko apna sasural samajh baithe hain, mahine mein do din aate hain aaram se so kar chale jaate hain aur bache taash khelte hain.",
    "complaint_text": "Master ji school ko apna sasural samajh baithe hain, mahine mein do din aate hain aaram se so kar chale jaate hain aur bache taash khelte hain.",
    "dialect": "Hindi",
    "expected_department": "basic_education",
    "expected_urgency": 3,
    "expected_hazard": False,
    "is_life_safety_hazard": False,
    "cluster_group": "BLY_TEACHER_SLEEPING"
  },
  {
    "id": "CMP-061",
    "text": "Kudos to PWD for building moon craters on our colony road so ISRO scientists can practice lunar rover landings right here in Kanpur!",
    "complaint_text": "Kudos to PWD for building moon craters on our colony road so ISRO scientists can practice lunar rover landings right here in Kanpur!",
    "dialect": "English",
    "expected_department": "pwd",
    "expected_urgency": 3,
    "expected_hazard": False,
    "is_life_safety_hazard": False,
    "cluster_group": "KNP_CRATER_POTHOLE"
  },
  {
    "id": "CMP-062",
    "text": "Ghar ke nal se badboodar peela soup nikal raha hai, Jal Nigam walo ko bula kar ye sharbat pila do tab inki aankhein khulengi!",
    "complaint_text": "Ghar ke nal se badboodar peela soup nikal raha hai, Jal Nigam walo ko bula kar ye sharbat pila do tab inki aankhein khulengi!",
    "dialect": "Hindi",
    "expected_department": "jal_nigam",
    "expected_urgency": 4,
    "expected_hazard": False,
    "is_life_safety_hazard": False,
    "cluster_group": "AGR_YELLOW_SOUP_TAP"
  },
  {
    "id": "CMP-063",
    "text": "Lekhpal sahab ko dhoondhne ke liye ab police mein gumshuda ki report darj karwani padegi, chhe mahine se chakmarg aakhya file dabakar baithe hain.",
    "complaint_text": "Lekhpal sahab ko dhoondhne ke liye ab police mein gumshuda ki report darj karwani padegi, chhe mahine se chakmarg aakhya file dabakar baithe hain.",
    "dialect": "Hindi",
    "expected_department": "revenue",
    "expected_urgency": 2,
    "expected_hazard": False,
    "is_life_safety_hazard": False,
    "cluster_group": "BND_MISSING_LEKHPAL"
  },
  {
    "id": "CMP-064",
    "text": "Mohalle ke kachre ke pahad ki khushbu ab drawing room tak aa rahi hai, safai karmiyon ko shahi daawat pe bulana padega tabhi kachra uthega kya?",
    "complaint_text": "Mohalle ke kachre ke pahad ki khushbu ab drawing room tak aa rahi hai, safai karmiyon ko shahi daawat pe bulana padega tabhi kachra uthega kya?",
    "dialect": "Hindi",
    "expected_department": "nagar_nigam",
    "expected_urgency": 3,
    "expected_hazard": False,
    "is_life_safety_hazard": False,
    "cluster_group": "GKP_SARCASTIC_GARBAGE"
  },
  {
    "id": "CMP-065",
    "text": "108 ambulance ko call karne par driver bola petrol nahi hai thela karke le aao, emergency service ke naam par majak bana rakha hai!",
    "complaint_text": "108 ambulance ko call karne par driver bola petrol nahi hai thela karke le aao, emergency service ke naam par majak bana rakha hai!",
    "dialect": "Hindi",
    "expected_department": "health",
    "expected_urgency": 4,
    "expected_hazard": False,
    "is_life_safety_hazard": False,
    "cluster_group": "PRY_AMBULANCE_PETROL"
  },
  {
    "id": "CMP-066",
    "text": "Gaon ki solar street light bas amavasya ke din decoration piece ban kar khadi rehti hai, ek din bhi light jali ho to batao!",
    "complaint_text": "Gaon ki solar street light bas amavasya ke din decoration piece ban kar khadi rehti hai, ek din bhi light jali ho to batao!",
    "dialect": "Hindi",
    "expected_department": "panchayati_raj",
    "expected_urgency": 2,
    "expected_hazard": False,
    "is_life_safety_hazard": False,
    "cluster_group": "SLT_DEAD_SOLAR_LIGHT"
  },
  {
    "id": "CMP-067",
    "text": "Anganwadi karyakarti bacho ka daliya apne ghar ke bhed bakriyo ko khila rahi hai aur bolti hai upar se ration nahi aaya!",
    "complaint_text": "Anganwadi karyakarti bacho ka daliya apne ghar ke bhed bakriyo ko khila rahi hai aur bolti hai upar se ration nahi aaya!",
    "dialect": "Hindi",
    "expected_department": "wcd",
    "expected_urgency": 3,
    "expected_hazard": False,
    "is_life_safety_hazard": False,
    "cluster_group": "MRT_DALIYA_GOATS"
  },
  {
    "id": "CMP-068",
    "text": "Streetlight pole number 14 ka bulb fuse ho gaya hai, please spare bulb laga kar check karwayein.",
    "complaint_text": "Streetlight pole number 14 ka bulb fuse ho gaya hai, please spare bulb laga kar check karwayein.",
    "dialect": "Hinglish",
    "expected_department": "panchayati_raj",
    "expected_urgency": 1,
    "expected_hazard": False,
    "is_life_safety_hazard": False,
    "cluster_group": "LKO_FUSED_BULB"
  },
  {
    "id": "CMP-069",
    "text": "Colony park ke walking track par rakhi hui ek wooden bench ka ek plank toot gaya hai, usko repair karwayein.",
    "complaint_text": "Colony park ke walking track par rakhi hui ek wooden bench ka ek plank toot gaya hai, usko repair karwayein.",
    "dialect": "Hinglish",
    "expected_department": "nagar_nigam",
    "expected_urgency": 1,
    "expected_hazard": False,
    "is_life_safety_hazard": False,
    "cluster_group": "NOI_PARK_BENCH"
  },
  {
    "id": "CMP-070",
    "text": "Khasra number 402 ki certified khatauni copy online download karne mein payment deduct ho gayi par slip nahi generate hui, process verify karein.",
    "complaint_text": "Khasra number 402 ki certified khatauni copy online download karne mein payment deduct ho gayi par slip nahi generate hui, process verify karein.",
    "dialect": "Hindi",
    "expected_department": "revenue",
    "expected_urgency": 2,
    "expected_hazard": False,
    "is_life_safety_hazard": False,
    "cluster_group": "ALH_KHATAUNI_SLIP"
  },
  {
    "id": "CMP-071",
    "text": "Padosi ke ghar mein birthday party chal rahi hai aur thoda loud music baj raha hai, request to kindly ask them to lower volume.",
    "complaint_text": "Padosi ke ghar mein birthday party chal rahi hai aur thoda loud music baj raha hai, request to kindly ask them to lower volume.",
    "dialect": "Hinglish",
    "expected_department": "police",
    "expected_urgency": 2,
    "expected_hazard": False,
    "is_life_safety_hazard": False,
    "cluster_group": "GZB_BIRTHDAY_MUSIC"
  },
  {
    "id": "CMP-072",
    "text": "Nagar Nigam property tax receipt par mera naam spelled incorrectly hai, Sharma ki jagah Verma print hua hai correction karwayein.",
    "complaint_text": "Nagar Nigam property tax receipt par mera naam spelled incorrectly hai, Sharma ki jagah Verma print hua hai correction karwayein.",
    "dialect": "Hinglish",
    "expected_department": "nagar_nigam",
    "expected_urgency": 1,
    "expected_hazard": False,
    "is_life_safety_hazard": False,
    "cluster_group": "AGR_TAX_NAME_FIX"
  },
  {
    "id": "CMP-073",
    "text": "Sub health center ke main board ka paint dhoop se feeka pad gaya hai, naya board lagwaya jaye taaki aane walo ko door se dikh sake.",
    "complaint_text": "Sub health center ke main board ka paint dhoop se feeka pad gaya hai, naya board lagwaya jaye taaki aane walo ko door se dikh sake.",
    "dialect": "Hindi",
    "expected_department": "health",
    "expected_urgency": 1,
    "expected_hazard": False,
    "is_life_safety_hazard": False,
    "cluster_group": "BAP_BOARD_PAINT"
  },
  {
    "id": "CMP-074",
    "text": "Prathmik vidyalaya ke main gate par rust lag gayi hai, grease aur oiling ki zaroorat hai jisse aawaz na kare.",
    "complaint_text": "Prathmik vidyalaya ke main gate par rust lag gayi hai, grease aur oiling ki zaroorat hai jisse aawaz na kare.",
    "dialect": "Hindi",
    "expected_department": "basic_education",
    "expected_urgency": 1,
    "expected_hazard": False,
    "is_life_safety_hazard": False,
    "cluster_group": "STP_GATE_GREASE"
  },
  {
    "id": "CMP-075",
    "text": "Electricity service connection transfer application form ka status portal par pending review dikha raha hai, expected timeline batayein.",
    "complaint_text": "Electricity service connection transfer application form ka status portal par pending review dikha raha hai, expected timeline batayein.",
    "dialect": "Hinglish",
    "expected_department": "uppcl",
    "expected_urgency": 2,
    "expected_hazard": False,
    "is_life_safety_hazard": False,
    "cluster_group": "LKO_CONNECTION_TIMELINE"
  }
]

combined = [x for x in existing if x["id"] not in {y["id"] for y in new_items}] + new_items
with open(eval_file, "w", encoding="utf-8") as f:
    json.dump(combined, f, ensure_ascii=False, indent=2)

print(f"Successfully wrote {len(combined)} complaints to {eval_file.name}")
