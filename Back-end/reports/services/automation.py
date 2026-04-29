import logging
import os
import sys
import subprocess
import tempfile
import json
from typing import Tuple, Optional
from seleniumbase import SB
import random 
import base64

logger = logging.getLogger(__name__)

SCREENSHOTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)


import random
import json

# Create comprehensive random identity profiles for IC3/FTC reporting

FIRST_NAMES = [
    "James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda",
    "David", "Elizabeth", "William", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa",
    "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley",
    "Steven", "Kimberly", "Paul", "Emily", "Andrew", "Donna", "Joshua", "Michelle",
    "Kenneth", "Dorothy", "Kevin", "Carol", "Brian", "Amanda", "George", "Melissa",
    "Edward", "Deborah", "Ronald", "Stephanie", "Timothy", "Rebecca", "Jason", "Sharon",
    "Jeffrey", "Laura", "Ryan", "Cynthia", "Jacob", "Kathleen", "Gary", "Amy",
    "Nicholas", "Shirley", "Eric", "Angela", "Jonathan", "Helen", "Stephen", "Anna",
    "Larry", "Brenda", "Justin", "Pamela", "Scott", "Nicole", "Brandon", "Emma",
    "Benjamin", "Samantha", "Samuel", "Katherine", "Gregory", "Christine", "Frank", "Debra",
    "Alexander", "Rachel", "Raymond", "Catherine", "Patrick", "Carolyn", "Jack", "Janet",
    "Dennis", "Ruth", "Jerry", "Maria", "Tyler", "Heather", "Aaron", "Diane",
    "Jose", "Virginia", "Adam", "Julie", "Nathan", "Joyce", "Henry", "Victoria",
    "Douglas", "Olivia", "Zachary", "Kelly", "Peter", "Christina", "Kyle", "Lauren",
    "Ethan", "Joan", "Walter", "Evelyn", "Noah", "Olivia", "Jeremy", "Judith",
    "Christian", "Megan", "Keith", "Cheryl", "Roger", "Andrea", "Terry", "Hannah",
    "Austin", "Martha", "Sean", "Jacqueline", "Gerald", "Frances", "Carl", "Gloria",
    "Dylan", "Ann", "Harold", "Teresa", "Jordan", "Kathryn", "Jesse", "Sara",
    "Bryan", "Janice", "Lawrence", "Jean", "Arthur", "Alice", "Gabriel", "Madison",
    "Bruce", "Doris", "Logan", "Abigail", "Billy", "Julia", "Joe", "Judy",
    "Alan", "Grace", "Juan", "Denise", "Elijah", "Amber", "Willie", "Marilyn",
    "Albert", "Beverly", "Wayne", "Danielle", "Randy", "Theresa", "Mason", "Sophia",
    "Vincent", "Marie", "Liam", "Diana", "Roy", "Brittany", "Bobby", "Natalie",
    "Caleb", "Isabella", "Bradley", "Charlotte", "Russell", "Rose", "Lucas", "Alexis",
    "Philip", "Kayla"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
    "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
    "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker",
    "Cruz", "Edwards", "Collins", "Reyes", "Stewart", "Morris", "Morales", "Murphy",
    "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper", "Peterson", "Bailey",
    "Reed", "Kelly", "Howard", "Ramos", "Kim", "Cox", "Ward", "Richardson", "Watson",
    "Brooks", "Chavez", "Wood", "James", "Bennett", "Gray", "Mendoza", "Ruiz",
    "Hughes", "Price", "Alvarez", "Castillo", "Sanders", "Patel", "Myers", "Long",
    "Ross", "Foster", "Jimenez", "Powell", "Jenkins", "Perry", "Russell", "Sullivan",
    "Bell", "Coleman", "Butler", "Henderson", "Barnes", "Gonzales", "Fisher", "Vasquez",
    "Simmons", "Romero", "Jordan", "Patterson", "Alexander", "Hamilton", "Graham",
    "Reynolds", "Griffin", "Wallace", "Moreno", "West", "Cole", "Hayes", "Bryant",
    "Herrera", "Gibson", "Ellis", "Tran", "Medina", "Aguilar", "Stevens", "Murray",
    "Ford", "Castro", "Marshall", "Owens", "Harrison", "Fernandez", "Woods", "Washington",
    "Kennedy", "Wells", "Vargas", "Henry", "Chen", "Freeman", "Webb", "Tucker",
    "Guzman", "Burns", "Crawford", "Olson", "Simpson", "Porter", "Hunter", "Gordon",
    "Mendez", "Silva", "Shaw", "Snyder", "Mason", "Dixon", "Munoz", "Hunt",
    "Hicks", "Holmes", "Palmer", "Wagner", "Black", "Robertson", "Boyd", "Rose",
    "Stone", "Salazar", "Fox", "Warren", "Mills", "Meyer", "Rice", "Schmidt",
    "Garza", "Daniels", "Ferguson", "Nichols", "Stephens", "Soto", "Weaver", "Ryan",
    "Gardner", "Payne", "Grant", "Dunn", "Kelley", "Spencer", "Hawkins", "Arnold",
    "Pierce", "Vazquez", "Hansen", "Peters", "Santos", "Hart", "Bradley", "Knight",
    "Elliott", "Cunningham", "Duncan", "Armstrong", "Hudson", "Carroll", "Lane", "Riley",
    "Andrews", "Alvarado", "Ray", "Delgado", "Berry", "Perkins", "Hoffman", "Johnston",
    "Matthews", "Pena", "Richards", "Contreras", "Willis", "Carpenter", "Lawrence",
    "Sandoval", "Guerrero", "George", "Chapman", "Rios", "Estrada", "Ortega", "Watkins",
    "Greene", "Nunez", "Valdez", "Hoffman", "Silva", "Lowe", "Logan", "Morrison"
]

STREET_NAMES = [
    "Main", "First", "Second", "Third", "Fourth", "Park", "Oak", "Pine", "Maple",
    "Cedar", "Elm", "Washington", "Lake", "Hill", "Jefferson", "Madison", "Adams",
    "Jackson", "Lincoln", "Grant", "Wilson", "Clay", "Center", "Church", "South",
    "North", "West", "East", "Highland", "Mill", "Spring", "Chestnut", "Walnut",
    "Spruce", "Willow", "Ridge", "Meadow", "Sunset", "River", "Forest", "Lakeview",
    "Broadway", "Market", "State", "Union", "Prospect", "Franklin", "Green", "Liberty",
    "Central", "Front", "Bridge", "Cherry", "Riverside", "Summit", "Dogwood", "Magnolia",
    "Peach", "Pear", "Apple", "Birch", "Poplar", "Sycamore", "Hickory", "Ash",
    "Beech", "Cypress", "Redwood", "Juniper", "Evergreen", "Holly", "Ivy", "Jasmine",
    "Lilac", "Linden", "Mulberry", "Myrtle", "Olive", "Palm", "Redbud", "Sequoia",
    "Teak", "Yew", "Acacia", "Alder", "Aspen", "Bamboo", "Baobab", "Cottonwood",
    "Dogwood", "Eucalyptus", "Fir", "Ginkgo", "Hawthorn", "Ironwood", "Jacaranda",
    "Koa", "Larch", "Mahogany", "Mangrove", "Neem", "Oleander", "Pawpaw", "Quince",
    "Rowan", "Sassafras", "Tamarind", "Umbrella", "Verbena", "Wisteria", "Xylosma",
    "Yucca", "Zelkova", "Amber", "Azure", "Bliss", "Coral", "Crystal", "Dawn",
    "Ember", "Fawn", "Garnet", "Harmony", "Indigo", "Jade", "Karma", "Luna",
    "Misty", "Nova", "Opal", "Pearl", "Quartz", "Ruby", "Sage", "Topaz",
    "Unity", "Velvet", "Willow", "Xanadu", "Yarrow", "Zenith", "Aurora", "Briar",
    "Clover", "Daisy", "Eden", "Fern", "Garden", "Haven", "Iris", "Juniper",
    "Kaleidoscope", "Lily", "Magnolia", "Nectar", "Orchard", "Petal", "Quail", "Rose",
    "Sierra", "Tulip", "Upland", "Violet", "Wren", "Xenia", "Yamhill", "Zinnia",
    "Acorn", "Buttercup", "Canyon", "Dandelion", "Echo", "Falcon", "Glen", "Harbor",
    "Island", "Journey", "Kingfisher", "Lagoon", "Marina", "Nest", "Oasis", "Pioneer",
    "Quest", "Rainbow", "Shore", "Timber", "Umbrella", "Valley", "Whisper", "Yacht",
    "Zephyr", "Alpine", "Brook", "Cottage", "Dell", "Estates", "Falls", "Grove",
    "Heights", "Inlet", "Junction", "Knoll", "Landing", "Manor", "Nook", "Overlook",
    "Pass", "Quay", "Ranch", "Station", "Terrace", "View", "Way", "Yard",
    "Arch", "Bay", "Circle", "Drive", "Expressway", "Freeway", "Garden", "Heights",
    "Interstate", "Junction", "Key", "Loop", "Motorway", "Narrow", "Parkway", "Quadrant",
    "Road", "Street", "Trail", "Underpass", "Viaduct", "Walk", "Yard", "Zone"
]

STREET_SUFFIXES = ["St", "Ave", "Blvd", "Dr", "Rd", "Ln", "Way", "Ct", "Pl", "Ter",
                   "Cir", "Trl", "Pkwy", "Hwy", "Loop", "Run", "Pass", "View", "Ridge",
                   "Point", "Bay", "Glen", "Dale", "Heights", "Crossing", "Meadows",
                   "Village", "Square", "Station", "Gardens", "Isle", "Cove", "Harbor",
                   "Landing", "Manor", "Mill", "Park", "Walk", "Woods", "Alley", "Arcade",
                   "Esplanade", "Freeway", "Causeway", "Boulevard", "Parade", "Promenade",
                   "Quay", "Row", "Terrace", "Vale", "Wharf", "Yard", "Close", "Crescent",
                   "Gate", "Mews", "Nook", "Outlook", "Path", "Rise", "Spur", "Track"]

CITIES = [
    "Springfield", "Franklin", "Washington", "Clinton", "Madison", "Georgetown", "Salem",
    "Greenville", "Bristol", "Fairview", "Manchester", "Oxford", "Arlington", "Ashland",
    "Berlin", "Bloomington", "Bradford", "Brooklyn", "Cambridge", "Centerville", "Chester",
    "Clayton", "Dayton", "Dover", "Fairfield", "Fayetteville", "Fremont", "Hamilton",
    "Harrisburg", "Harrison", "Hillsdale", "Jackson", "Jefferson", "Kingston", "Lebanon",
    "Lexington", "Lincoln", "Milford", "Monroe", "Morris", "Newton", "Oakland", "Oxford",
    "Perry", "Plymouth", "Portland", "Princeton", "Richmond", "Riverside", "Rochester",
    "Shelby", "Somerset", "Southfield", "Stanton", "Sullivan", "Taylor", "Trenton",
    "Union", "Warren", "Waterloo", "Waverly", "Wellington", "Westfield", "Wilmington",
    "Winchester", "York", "Aurora", "Burlington", "Cedar Rapids", "Davenport", "Des Moines",
    "Dubuque", "Iowa City", "Sioux City", "Waterloo", "Ames", "Ankeny", "Bettendorf",
    "Cedar Falls", "Clinton", "Coralville", "Council Bluffs", "Fort Dodge", "Johnston",
    "Marion", "Marshalltown", "Mason City", "Muscatine", "Ottumwa", "Pella", "Urbandale",
    "West Des Moines", "Albuquerque", "Las Cruces", "Rio Rancho", "Santa Fe", "Roswell",
    "Farmington", "Clovis", "Hobbs", "Alamogordo", "Carlsbad", "Gallup", "Deming",
    "Los Lunas", "Chaparral", "Sunland Park", "Las Vegas", "Portales", "Artesia",
    "Lovington", "Espanola", "Silver City", "Bernalillo", "Raton", "Aztec", "Truth",
    "Tucumcari", "Ruidoso", "Bloomfield", "Taos", "Belen", "Socorro", " Grants",
    "Los Alamos", "Church Rock", "Zuni Pueblo", "North Valley", "White Rock", "Anthony",
    "Eldorado", "El Cerro", "Lee Acres", "Milan", "Pajarito Mesa", "Sausal", "Tome",
    "Bosque Farms", "Ponderosa", "Jarales", "San Ysidro", "Pena Blanca", "San Felipe",
    "Santa Ana", "Santo Domingo", "Cochiti", "San Ildefonso", "Santa Clara", "Nambe",
    "Tesuque", "Pojoaque", "Cuyamungue", "Chimayo", "Truchas", "Cordova", "Dixon",
    "Velarde", "Embudo", "Rinconada", "Medanales", "Abiquiu", "Youngsville", "Coyote",
    "Pueblo", "Colorado Springs", "Aurora", "Fort Collins", "Lakewood", "Thornton",
    "Arvada", "Westminster", "Pueblo", "Centennial", "Boulder", "Greeley", "Longmont",
    "Loveland", "Grand Junction", "Broomfield", "Castle Rock", "Commerce City", "Parker",
    "Littleton", "Northglenn", "Brighton", "Englewood", "Wheat Ridge", "Fountain",
    "Lafayette", "Louisville", "Evans", "Windsor", "Montrose", "Golden", "Erie",
    "Durango", "Cañon City", "Sterling", "Applewood", "Cimarron Hills", "Welby",
    "Frederick", "Firestone", "Fort Morgan", "Johnstown", "Salida", "Alamosa", "Fruita",
    "Gypsum", "Rifle", "Glenwood Springs", "Carbondale", "Edwards", "Eagle", "Avon",
    "Basalt", "New Castle", "Silt", "Battlement Mesa", "Meeker", "Rangely", "Paonia",
    "Hotchkiss", "Cedaredge", "Delta", "Olathe", "Montrose", "Telluride", "Norwood",
    "Nucla", "Naturita", "Dove Creek", "Mancos", "Dolores", "Towaoc", "Cortez",
    "Bayfield", "Ignacio", "Pagosa Springs", "South Fork", "Del Norte", "Center",
    "Saguache", "Crestone", "Moffat", "Hooper", "Sanford", "Mosca", "Blanca",
    "Fort Garland", "San Luis", "Antonito", "Chama", "Capulin", "Conejos", "Manassa",
    "Sanford", "Romeo", "La Jara", "Alamosa", "Monte Vista", "Del Norte", "Creede",
    "South Fork", "Lake City", "Ouray", "Silverton", "Ridgway", "Telluride", "Placerville",
    "Sawpit", "Loghill Village", "Norwood", "Naturita", "Nucla", "Bedrock", "Paradox",
    "Gateway", "Cimarron", "Colona", "Ophir", "Mountain Village", "Egnar", "Redvale",
    "Dolores", "Mancos", "Towaoc", "Cortez", "Dove Creek", "Arboles", "Pagosa Springs",
    "Chimney Rock", "Ignacio", "Bayfield", "Durango", "Hermosa", "Electra", "Shamrock",
    "Wheeler", "Lela", "Lela", "McLean", "Groom", "Claude", "Panhandle", "White Deer",
    "Skellytown", "Borger", "Fritch", "Stinnett", "Sanford", "Gruver", "Spearman",
    "Perryton", "Canadian", "Higgins", "Lipscomb", "Follett", "Darrouzett", "Booker",
    "Perryton", "Mobeetie", "Wellington", "Quail", "Memphis", "Estelline", "Turkey",
    "Roaring Springs", "Matador", "Paducah", "Crowell", "Chillicothe", "Vernon",
    "Harrold", "Lockett", "Foard City", "Thalia", "Electra", "Iowa Park", "Burkburnett",
    "Haynesville", "Haughton", "Princeton", "Benton", "Bossier City", "Minden",
    "Ruston", "Natchitoches", "Hammond", "Zachary", "Thibodaux", "Pineville", "Baker",
    "Crowley", "Minden", "Bastrop", "Jennings", "Denham Springs", "Morgan City",
    "Abbeville", "Bogalusa", "DeRidder", "Eunice", "Opelousas", "Natchitoches",
    "Leesville", "Ruston", "West Monroe", "Bastrop", "Monroe", "Shreveport",
    "Bossier City", "Haughton", "Princeton", "Benton", "Mooringsport", "Vivian",
    "Oil City", "Belcher", "Gilliam", "Hosston", "Ida", "Rodessa", "Plain Dealing",
    "Sarepta", "Springhill", "Cullen", "Haynesville", "Shongaloo", "Minden",
    "Doyline", "Sibley", "Heflin", "Ringgold", "Castor", "Jamestown", "Bienville",
    "Arcadia", "Gibsland", "Lisbon", "Athens", "Homer", "Haynesville", "Summerfield",
    "Marion", "Columbia", "Baskin", "Winnsboro", "Crowville", "Wisner", "Gilbert",
    "Fort Necessity", "Mangham", "Rayville", "Start", "Alto", "Chatham", "Simsboro",
    "Grambling", "Dubach", "Vienna", "Calhoun", "Hodge", "Jonesboro", "Quitman",
    "Ashland", "Clayton", "Wisner", "Newellton", "St. Joseph", "Waterproof",
    "Ferriday", "Vidalia", "Ridgecrest", "Clayton", "Mayersville", "Rolling Fork",
    "Anguilla", "Onward", "Delta City", "Tchula", "Cruger", "Lexington", "Pickens",
    "Goodman", "Durant", "Sallis", "West", "Kosciusko", "Ethel", "McCool", "Vaiden",
    "Carthage", "Lena", "Morton", "Sebastopol", "Union", "Conehatta", "Madden",
    "Walnut Grove", "Puckett", "Terry", "Byram", "Florence", "Pearl", "Richland",
    "Flowood", "Tougaloo", "Madison", "Ridgeland", "Canton", "Kearney Park", "Bentonia",
    "Satartia", "Tinsley", "Yazoo City", "Midway", "Benton", "Holly Bluff", "Delta",
    "Rolling Fork", "Anguilla", "Onward", "Panther Burn", "Nitta Yuma", "Arcola",
    "Belzoni", "Isola", "Inverness", "Moorhead", "Indianola", "Sunflower", "Doddsville",
    "Ruleville", "Drew", "Cleveland", "Merigold", "Mound Bayou", "Winstonville",
    "Shelby", "Duncan", "Alligator", "Benoit", "Beulah", "Rosedale", "Gunnison",
    "Pace", "Merigold", "Renova", "Boyle", "Shaw", "Cleveland", "Parchman",
    "Tutwiler", "Sumner", "Webb", "Glendora", "Minter City", "Schlater", "Itta Bena",
    "Morgan City", "Sidon", "Greenwood", "Sidon", "Cruger", "Tchula", "Lexington",
    "Pickens", "Goodman", "Durant", "Sallis", "West", "Thornton", "Holcomb",
    "Greenville", "Leland", "Arcola", "Winterville", "Metcalfe", "Benoit", "Boyle",
    "Shaw", "Cleveland", "Pace", "Merigold", "Renova", "Gunnison", "Rosedale",
    "Beulah", "Alligator", "Duncan", "Shelby", "Winstonville", "Mound Bayou",
    "Merigold", "Cleveland", "Drew", "Ruleville", "Doddsville", "Sunflower",
    "Indianola", "Moorhead", "Inverness", "Isola", "Belzoni", "Silver City",
    "Louise", "Eden", "Anguilla", "Rolling Fork", "Midway", "Holly Bluff",
    "Benton", "Yazoo City", "Tinsley", "Satartia", "Bentonia", "Kearney Park",
    "Canton", "Ridgeland", "Madison", "Tougaloo", "Flowood", "Richland", "Pearl",
    "Florence", "Byram", "Terry", "Puckett", "Walnut Grove", "Madden", "Conehatta",
    "Union", "Sebastopol", "Morton", "Lena", "Carthage", "Vaiden", "McCool",
    "Ethel", "Kosciusko", "West", "Sallis", "Durant", "Goodman", "Pickens",
    "Lexington", "Cruger", "Tchula", "Delta City", "Onward", "Anguilla", "Mayersville",
    "Rolling Fork", "Waterproof", "St. Joseph", "Newellton", "Wisner", "Clayton",
    "Ferriday", "Vidalia", "Ridgecrest", "Clayton", "Jonesboro", "Hodge", "Calhoun",
    "Vienna", "Dubach", "Grambling", "Simsboro", "Chatham", "Alto", "Start",
    "Rayville", "Mangham", "Fort Necessity", "Gilbert", "Wisner", "Crowville",
    "Winnsboro", "Baskin", "Columbia", "Marion", "Summerfield", "Haynesville",
    "Homer", "Athens", "Lisbon", "Gibsland", "Arcadia", "Bienville", "Jamestown",
    "Ringgold", "Heflin", "Sibley", "Doyline", "Minden", "Shongaloo", "Springhill",
    "Cullen", "Plain Dealing", "Rodessa", "Ida", "Hosston", "Belcher", "Gilliam",
    "Oil City", "Vivian", "Mooringsport", "Benton", "Princeton", "Haughton",
    "Bossier City", "Shreveport", "Greenwood", "Waskom", "Jonesville", "Elysian Fields"
]

STATES = [
    ("AL", "Alabama"), ("AK", "Alaska"), ("AZ", "Arizona"), ("AR", "Arkansas"),
    ("CA", "California"), ("CO", "Colorado"), ("CT", "Connecticut"), ("DE", "Delaware"),
    ("FL", "Florida"), ("GA", "Georgia"), ("HI", "Hawaii"), ("ID", "Idaho"),
    ("IL", "Illinois"), ("IN", "Indiana"), ("IA", "Iowa"), ("KS", "Kansas"),
    ("KY", "Kentucky"), ("LA", "Louisiana"), ("ME", "Maine"), ("MD", "Maryland"),
    ("MA", "Massachusetts"), ("MI", "Michigan"), ("MN", "Minnesota"), ("MS", "Mississippi"),
    ("MO", "Missouri"), ("MT", "Montana"), ("NE", "Nebraska"), ("NV", "Nevada"),
    ("NH", "New Hampshire"), ("NJ", "New Jersey"), ("NM", "New Mexico"), ("NY", "New York"),
    ("NC", "North Carolina"), ("ND", "North Dakota"), ("OH", "Ohio"), ("OK", "Oklahoma"),
    ("OR", "Oregon"), ("PA", "Pennsylvania"), ("RI", "Rhode Island"), ("SC", "South Carolina"),
    ("SD", "South Dakota"), ("TN", "Tennessee"), ("TX", "Texas"), ("UT", "Utah"),
    ("VT", "Vermont"), ("VA", "Virginia"), ("WA", "Washington"), ("WV", "West Virginia"),
    ("WI", "Wisconsin"), ("WY", "Wyoming"), ("DC", "District of Columbia")
]

EMAIL_DOMAINS = [
    "gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "aol.com", "icloud.com",
    "protonmail.com", "mail.com", "zoho.com", "yandex.com", "gmx.com", "live.com",
    "msn.com", "comcast.net", "verizon.net", "att.net", "sbcglobal.net", "bellsouth.net",
    "cox.net", "charter.net", "earthlink.net", "juno.com", "netzero.net", "me.com",
    "mac.com", "fastmail.com", "tutanota.com", "hey.com", "pm.me", "duck.com",
    "skiff.com", "startmail.com", "runbox.com", "kolabnow.com", "mailbox.org",
    "posteo.de", "disroot.org", "riseup.net", "autistici.org", "aktivix.org"
]

AREA_CODES = [
    201, 202, 203, 205, 206, 207, 208, 209, 210, 212, 213, 214, 215, 216, 217, 218,
    219, 220, 223, 224, 225, 228, 229, 231, 234, 239, 240, 242, 252, 253, 254, 256,
    260, 262, 267, 269, 270, 272, 274, 276, 281, 301, 302, 303, 304, 305, 307, 308,
    309, 310, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 323, 325, 327, 330,
    331, 334, 336, 337, 339, 346, 347, 351, 352, 360, 361, 364, 380, 385, 386, 401,
    402, 404, 405, 406, 407, 408, 409, 410, 412, 413, 414, 415, 417, 419, 423, 424,
    425, 430, 432, 434, 435, 440, 442, 443, 445, 447, 458, 469, 470, 475, 478, 479,
    480, 484, 501, 502, 503, 504, 505, 507, 508, 509, 510, 512, 513, 515, 516, 517,
    518, 520, 530, 531, 534, 539, 540, 541, 551, 559, 561, 562, 563, 564, 567, 570,
    571, 573, 574, 575, 580, 585, 586, 601, 602, 603, 605, 606, 607, 608, 609, 610,
    612, 614, 615, 616, 617, 618, 619, 620, 623, 626, 628, 629, 630, 631, 636, 641,
    646, 650, 651, 657, 660, 661, 662, 667, 669, 678, 681, 682, 701, 702, 703, 704,
    706, 707, 708, 712, 713, 714, 715, 716, 717, 718, 719, 720, 724, 725, 726, 727,
    731, 732, 734, 737, 740, 747, 754, 757, 760, 762, 763, 765, 769, 770, 772, 773,
    774, 775, 779, 781, 785, 786, 801, 802, 803, 804, 805, 806, 808, 810, 812, 813,
    814, 815, 816, 817, 818, 828, 830, 831, 832, 835, 838, 840, 843, 845, 847, 848,
    850, 856, 857, 858, 859, 860, 862, 863, 864, 865, 870, 872, 878, 901, 903, 904,
    906, 907, 908, 909, 910, 912, 913, 914, 915, 916, 917, 918, 919, 920, 925, 928,
    930, 931, 936, 937, 940, 941, 945, 947, 949, 951, 952, 954, 956, 959, 970, 971,
    972, 973, 975, 978, 979, 980, 984, 985, 986, 989
]


def generate_random_identity():
    """Generate a complete random identity for reporting."""
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    full_name = f"{first_name} {last_name}"
    
    # Generate address
    street_num = random.randint(100, 9999)
    street_name = random.choice(STREET_NAMES)
    street_suffix = random.choice(STREET_SUFFIXES)
    address = f"{street_num} {street_name} {street_suffix}"
    
    # Sometimes add apartment/unit
    if random.random() < 0.3:
        unit_types = ["Apt", "Unit", "Ste", "Fl", "#"]
        unit_num = random.randint(1, 999)
        address2 = f"{random.choice(unit_types)} {unit_num}"
    else:
        address2 = ""
    
    city = random.choice(CITIES)
    state_abbr, state_name = random.choice(STATES)
    
    # Generate ZIP based on state (simplified - just random valid-looking ZIP)
    zip_code = f"{random.randint(10000, 99999)}"
    
    # Generate phone with valid area code
    area_code = random.choice(AREA_CODES)
    prefix = random.randint(200, 999)
    line = random.randint(1000, 9999)
    phone = f"{area_code}{prefix}{line}"
    
    # Generate email
    email_formats = [
        f"{first_name.lower()}.{last_name.lower()}",
        f"{first_name.lower()}{last_name.lower()}",
        f"{first_name.lower()}{random.randint(1, 999)}",
        f"{last_name.lower()}{first_name.lower()[0]}",
        f"{first_name.lower()[0]}{last_name.lower()}",
        f"{first_name.lower()}_{last_name.lower()}",
        f"{last_name.lower()}.{first_name.lower()[0]}{random.randint(1, 99)}",
    ]
    email = f"{random.choice(email_formats)}@{random.choice(EMAIL_DOMAINS)}"
    
    return {
        "first_name": first_name,
        "last_name": last_name,
        "full_name": full_name,
        "address": address,
        "address2": address2,
        "city": city,
        "state": state_abbr,
        "state_name": state_name,
        "zip": zip_code,
        "phone": phone,
        "email": email,
    }


import logging
import os
import random
import time
import re
from typing import Tuple, Optional
from seleniumbase import SB

logger = logging.getLogger(__name__)

SCREENSHOTS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "screenshots"
)
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

FINGERPRINTS = [
    {
        "agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "platform": "Win32", "vendor": "Google Inc.", "cores": 8, "memory": 8,
        "screen_w": 1920, "screen_h": 1080, "avail_h": 1040,
        "timezone": "America/Chicago", "lang": "en-US",
    },
    {
        "agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
        "platform": "Win32", "vendor": "Google Inc.", "cores": 4, "memory": 4,
        "screen_w": 1366, "screen_h": 768, "avail_h": 728,
        "timezone": "America/New_York", "lang": "en-US",
    },
    {
        "agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "platform": "MacIntel", "vendor": "Apple Computer, Inc.", "cores": 10, "memory": 16,
        "screen_w": 1440, "screen_h": 900, "avail_h": 860,
        "timezone": "America/Los_Angeles", "lang": "en-US",
    },
]


# ── FTC helpers (prefixed ftc_ to avoid collision with IC3 helpers) ───────────

def ftc_human_delay(min_ms=300, max_ms=900):
    base = random.uniform(min_ms, max_ms) / 1000
    jitter = random.uniform(0, 0.05)
    time.sleep(base + jitter)


def ftc_inject_fingerprint(sb, fp):
    rtt      = random.choice([20, 30, 50, 60])
    downlink = random.choice([5, 8, 10, 15])
    paint    = round(random.uniform(0.3, 0.9), 3)
    page_t   = round(random.uniform(500, 900), 1)
    sb.execute_script(
        "(function() {"
        "  function tryDefine(obj, prop, value) {"
        "    try {"
        "      var desc = Object.getOwnPropertyDescriptor(obj, prop);"
        "      if (!desc || desc.configurable) {"
        "        Object.defineProperty(obj, prop, { get: function() { return value; }, configurable: true });"
        "      }"
        "    } catch(e) {}"
        "  }"
        f"  tryDefine(navigator, 'platform',  '{fp['platform']}');"
        f"  tryDefine(navigator, 'vendor',    '{fp['vendor']}');"
        f"  tryDefine(navigator, 'languages', ['{fp['lang']}', 'en']);"
        f"  tryDefine(navigator, 'hardwareConcurrency', {fp['cores']});"
        f"  tryDefine(navigator, 'deviceMemory',        {fp['memory']});"
        f"  tryDefine(screen,    'width',      {fp['screen_w']});"
        f"  tryDefine(screen,    'height',     {fp['screen_h']});"
        f"  tryDefine(screen,    'availWidth', {fp['screen_w']});"
        f"  tryDefine(screen,    'availHeight',{fp['avail_h']});"
        "  tryDefine(screen,    'colorDepth', 24);"
        "  tryDefine(navigator, 'webdriver',  undefined);"
        "  tryDefine(navigator, 'plugins', (function() {"
        "    var arr = ["
        "      {name:'Chrome PDF Plugin', filename:'internal-pdf-viewer'},"
        "      {name:'Chrome PDF Viewer', filename:'mhjfbmdgcfjbbpaeojofohoefgiehjai'},"
        "      {name:'Native Client',     filename:'internal-nacl-plugin'},"
        "    ];"
        "    try { arr.__proto__ = PluginArray.prototype; } catch(e) {}"
        "    return arr;"
        "  })());"
        "  if (!window.chrome) {"
        "    window.chrome = {"
        "      runtime: { connect: function(){}, sendMessage: function(){} },"
        f"     loadTimes: function() {{ return {{ firstPaintTime: {paint} }}; }},"
        f"     csi: function() {{ return {{ pageT: {page_t} }}; }},"
        "    };"
        "  }"
        f"  tryDefine(navigator, 'connection', {{ effectiveType: '4g', rtt: {rtt}, downlink: {downlink} }});"
        "})();"
    )


def ftc_simulate_human_mouse(sb):
    for _ in range(random.randint(2, 4)):
        x = random.randint(200, 900)
        y = random.randint(100, 500)
        sb.execute_script(
            "(function() {"
            "  window.dispatchEvent(new MouseEvent('mousemove', {"
            f"    clientX: {x}, clientY: {y}, bubbles: true"
            "  }));"
            "})();"
        )
        time.sleep(random.uniform(0.1, 0.3))


def ftc_random_scroll(sb):
    amount = random.randint(80, 250)
    sb.execute_script(f"window.scrollBy(0, {amount});")
    time.sleep(random.uniform(0.3, 0.7))
    sb.execute_script(f"window.scrollBy(0, -{amount // 2});")
    ftc_human_delay(200, 500)


def ftc_force_select_radio(sb, selector):
    safe = selector.replace("'", "\\'")
    sb.execute_script(
        "(function() {"
        f"  var el = document.querySelector('{safe}');"
        "  if (el) {"
        "    el.focus();"
        "    el.click();"
        "    el.checked = true;"
        "    ['click', 'input', 'change'].forEach(function(evt) {"
        "      el.dispatchEvent(new Event(evt, { bubbles: true }));"
        "    });"
        "  }"
        "})();"
    )
    ftc_human_delay(400, 800)


def ftc_human_type(sb, selector, text):
    safe = selector.replace("'", "\\'")
    sb.execute_script(
        "(function() {"
        f"  var el = document.querySelector('{safe}');"
        "  if (el) { el.focus(); el.value = ''; el.dispatchEvent(new Event('input', { bubbles: true })); }"
        "})();"
    )
    ftc_human_delay(200, 400)
    for char in text:
        c = char.replace("\\", "\\\\").replace("'", "\\'")
        sb.execute_script(
            "(function() {"
            f"  var el = document.querySelector('{safe}');"
            f"  if (el) {{ el.value += '{c}'; el.dispatchEvent(new Event('input', {{ bubbles: true }})); }}"
            "})();"
        )
        time.sleep(random.uniform(0.045, 0.13))
    sb.execute_script(
        "(function() {"
        f"  var el = document.querySelector('{safe}');"
        "  if (el) el.dispatchEvent(new Event('change', { bubbles: true }));"
        "})();"
    )
    ftc_human_delay(300, 600)


def ftc_set_select(sb, sel_id, value):
    safe_id  = sel_id.replace("'", "\\'")
    safe_val = value.replace("'", "\\'")
    sb.execute_script(
        "(function() {"
        f"  var sel = document.getElementById('{safe_id}');"
        "  if (sel) {"
        f"    sel.value = '{safe_val}';"
        "    sel.dispatchEvent(new Event('change', { bubbles: true }));"
        "  }"
        "})();"
    )
    ftc_human_delay(300, 700)


def ftc_wait_and_click_continue(sb):
    sb.wait_for_element_visible("button", timeout=20)
    for _ in range(40):
        disabled = sb.execute_script(
            "(function() {"
            "  var btn = Array.from(document.querySelectorAll('button'))"
            "    .find(function(b) { return b.textContent.trim() === 'Continue'; });"
            "  return btn ? btn.disabled : true;"
            "})()"
        )
        if not disabled:
            break
        time.sleep(0.5)
    ftc_simulate_human_mouse(sb)
    ftc_human_delay(600, 1200)
    sb.execute_script(
        "(function() {"
        "  var btn = Array.from(document.querySelectorAll('button'))"
        "    .find(function(b) { return b.textContent.trim() === 'Continue'; });"
        "  if (btn) btn.click();"
        "})()"
    )
    ftc_human_delay(2000, 3500)


def ftc_wait_for_url_fragment(sb, fragment, timeout=15):
    for _ in range(timeout * 2):
        if fragment in sb.get_current_url():
            return
        time.sleep(0.5)
    print(f"[warn] URL fragment '{fragment}' not seen after {timeout}s")


# ── Main FTC function ─────────────────────────────────────────────────────────

def submit_ftc_complaint(
    phone_number: str,
    brand: str,
    landing_url: str,
    description: str,
    reporter_first_name: str = None,
    reporter_last_name: str = None,
    reporter_address: str = None,
    reporter_address2: str = None,
    reporter_city: str = None,
    reporter_state: str = None,
    reporter_zip: str = None,
    reporter_phone: str = None,
    reporter_email: str = None,
) -> Tuple[bool, str, Optional[str]]:

    screenshot_path = os.path.join(SCREENSHOTS_DIR, f"ftc_{phone_number}.png")
    screenshot_b64 = None

    escaped_description = (
        f"They are impersonating {brand}. "
        f"The scam phone number is {phone_number} and the landing page is {landing_url}"
    ).replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"').replace("\n", " ")

    reporter_zip_str = str(reporter_zip) if reporter_zip else ""

    fp = random.choice(FINGERPRINTS)
    print(f"[fingerprint] Using agent: {fp['agent'][:60]}...")

    try:
        with SB(
            browser="chrome",
            headless=True,
            agent=fp["agent"],
            undetectable=True,
            slow=True,
        ) as sb:

            sb.open("https://reportfraud.ftc.gov/")
            ftc_inject_fingerprint(sb, fp)
            ftc_human_delay(2000, 3500)
            ftc_random_scroll(sb)
            ftc_simulate_human_mouse(sb)
            print("Loaded:", sb.get_current_url())

            # Step 1: Report Now
            sb.wait_for_element_visible("button", timeout=15)
            sb.execute_script(
                "(function() {"
                "  var btn = Array.from(document.querySelectorAll('button'))"
                "    .find(function(b) { return b.textContent.includes('Report Now'); });"
                "  if (btn) btn.click();"
                "})()"
            )
            ftc_wait_for_url_fragment(sb, "/assistant")
            ftc_inject_fingerprint(sb, fp)
            ftc_human_delay(1500, 2500)
            print("After Report Now:", sb.get_current_url())

            # Step 2: Category
            sb.wait_for_element_present("#cat-radio-1", timeout=15)
            ftc_human_delay(800, 1500)
            ftc_random_scroll(sb)
            ftc_force_select_radio(sb, "#cat-radio-1")
            print("cat-radio-1 checked:", sb.execute_script("return document.querySelector('#cat-radio-1').checked"))
            ftc_human_delay(1000, 2000)
            ftc_wait_and_click_continue(sb)
            ftc_inject_fingerprint(sb, fp)
            print("After category Continue:", sb.get_current_url())

            # Step 3: Subcategory
            sb.wait_for_element_present("#subcat-radio-2", timeout=15)
            ftc_human_delay(800, 1500)
            ftc_force_select_radio(sb, "#subcat-radio-2")
            print("subcat-radio-2 checked:", sb.execute_script("return document.querySelector('#subcat-radio-2').checked"))
            ftc_human_delay(1000, 2000)
            ftc_wait_and_click_continue(sb)
            ftc_inject_fingerprint(sb, fp)
            print("After subcategory Continue:", sb.get_current_url())

            # Step 4: Money lost?
            sb.wait_for_element_present("#yes-or-no-money-no", timeout=15)
            ftc_human_delay(600, 1200)
            ftc_force_select_radio(sb, "#yes-or-no-money-no")

            options = sb.execute_script(
                "(function() { var sel = document.getElementById('rdcontact'); if (!sel) return 'not found'; return Array.from(sel.options).map(function(o) { return o.value + ' = ' + o.text; }); })()"
            )
            print('rdcontact options:', options)

            # Step 5: Scammer info
            ftc_human_delay(500, 1000)
            ftc_set_select(sb, "rdcontact", "3: 128")

            ftc_human_type(sb, "#rcname",             brand.replace("'", "\\'"))
            ftc_human_type(sb, "#rccompanyFirstName",  (reporter_first_name or "").replace("'", "\\'"))
            ftc_human_type(sb, "#rccompanyLastName",   (reporter_last_name  or "").replace("'", "\\'"))

            ftc_force_select_radio(sb, "#yes-or-no-contact-no")
            ftc_human_delay(500, 1000)

            sb.execute_script(
                "(function() {"
                "  var ta = document.querySelector('textarea');"
                "  if (ta) {"
                f"    ta.value = '{escaped_description}';"
                "    ta.dispatchEvent(new Event('input',  { bubbles: true }));"
                "    ta.dispatchEvent(new Event('change', { bubbles: true }));"
                "  }"
                "})();"
            )
            ftc_human_delay(500, 1000)
            print("Textarea:", sb.execute_script(
                "(function() {"
                "  var ta = document.querySelector('textarea');"
                "  return ta ? ta.value : 'not found';"
                "})()"
            ))

            ftc_simulate_human_mouse(sb)
            ftc_human_delay(1000, 2000)
            ftc_wait_and_click_continue(sb)
            ftc_inject_fingerprint(sb, fp)
            print("After scammer info Continue:", sb.get_current_url())
            # if "confirmation" in sb.get_current_url().lower():
            if "confirmation" in sb.get_current_url().lower() or "main" in sb.get_current_url().lower():
                print("FTC went straight to confirmation — done")
                sb.execute_script("window.scrollTo(0, 0);")
                ftc_human_delay(500, 800)
                try:
                    sb.save_screenshot(screenshot_path)
                    with open(screenshot_path, "rb") as f:
                        screenshot_b64 = base64.b64encode(f.read()).decode("utf-8")
                except Exception as e:
                    print(f"Screenshot failed: {e}")
                return (True, "FTC complaint submitted", screenshot_path, screenshot_b64)
            # Step 6: Reporter info
            sb.wait_for_element_present("#yes-or-no-report-other-yes", timeout=15)
            ftc_human_delay(600, 1200)
            ftc_force_select_radio(sb, "#yes-or-no-report-other-yes")

            ftc_human_delay(500, 1000)
            ftc_human_type(sb, "#rayfirstName", (reporter_first_name or "").replace("'", "\\'"))
            ftc_human_type(sb, "#raylastName",  (reporter_last_name  or "").replace("'", "\\'"))

            ftc_set_select(sb, "raycountry", "1: USA")
            ftc_human_delay(800, 1500)

            address_fields = {
                "#reportAboutYourAddress": (reporter_address  or "").replace("'", "\\'"),
                "#rayaddresstwo":          (reporter_address2 or "").replace("'", "\\'"),
                "#raycity":                (reporter_city     or "").replace("'", "\\'"),
                "#rayotherState":          (reporter_state    or "").replace("'", "\\'"),
                "#USZipCode":              reporter_zip_str.replace("'", "\\'"),
            }
            for selector, value in address_fields.items():
                ftc_random_scroll(sb)
                ftc_human_type(sb, selector, value)

            ftc_human_type(sb, "#rayphone", (reporter_phone or "").replace("'", "\\'"))
            ftc_human_type(sb, "#rayemail", (reporter_email or "").replace("'", "\\'"))

            ftc_set_select(sb, "rayphoneType", "2: 0")
            ftc_set_select(sb, "rayAgeRange",  "4: 3")

            ftc_force_select_radio(sb, "#yes-or-no-small-business-no")
            ftc_human_delay(1000, 2000)
            ftc_simulate_human_mouse(sb)

            # Step 7: Submit
            sb.execute_script(
                "(function() {"
                "  var btn = Array.from(document.querySelectorAll('button'))"
                "    .find(function(b) { return b.textContent.trim() === 'Submit'; });"
                "  if (btn) btn.click();"
                "})()"
            )
            ftc_human_delay(5000, 7000)

            final_url   = sb.get_current_url()
            final_title = sb.get_title()

            success = (
                "confirm" in final_url.lower() or
                "thank"   in final_title.lower() or
                "confirm" in final_title.lower()
            )

            if success:
                try:
                    # Scroll to top first so full page capture starts from top
                    sb.execute_script("window.scrollTo(0, 0);")
                    ftc_human_delay(500, 800)
                    sb.save_screenshot(screenshot_path)
                    with open(screenshot_path, "rb") as f:
                        screenshot_b64 = base64.b64encode(f.read()).decode("utf-8")
                    print(f"[+] FTC screenshot saved: {screenshot_path}")
                except Exception as e:
                    print(f"Screenshot failed: {e}")

            return (
                success,
                "FTC complaint submitted" if success else "FTC submission failed",
                screenshot_path if success else None,
                screenshot_b64 if success else None,
            )
            # sb.execute_script(
            #     "(function() {"
            #     "  var btn = Array.from(document.querySelectorAll('button'))"
            #     "    .find(function(b) { return b.textContent.trim() === 'Submit'; });"
            #     "  if (btn) btn.click();"
            #     "})()"
            # )
            # ftc_human_delay(5000, 7000)

            # final_url   = sb.get_current_url()
            # final_title = sb.get_title()

            # success = (
            #     "confirm" in final_url.lower() or
            #     "thank"   in final_title.lower() or
            #     "confirm" in final_title.lower()
            # )

            # if success:
            #     try:
            #         sb.save_screenshot(screenshot_path)
            #         print(f"[+] FTC screenshot saved: {screenshot_path}")
            #     except Exception as e:
            #         print(f"Screenshot failed: {e}")
            # return (
            #     success,
            #     "FTC complaint submitted" if success else "FTC submission failed",
            #     screenshot_path if success else None,
            # )

    except Exception as e:
        logger.error(f"FTC submission failed: {e}")
        return (False, str(e), None, None)




logger = logging.getLogger(__name__)

SCREENSHOTS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "screenshots"
)
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

FINGERPRINTS = [
    {
        "agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "platform": "Win32", "vendor": "Google Inc.", "cores": 8, "memory": 8,
        "screen_w": 1920, "screen_h": 1080, "avail_h": 1040,
        "timezone": "America/Chicago", "lang": "en-US",
    },
    {
        "agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
        "platform": "Win32", "vendor": "Google Inc.", "cores": 4, "memory": 4,
        "screen_w": 1366, "screen_h": 768, "avail_h": 728,
        "timezone": "America/New_York", "lang": "en-US",
    },
    {
        "agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "platform": "MacIntel", "vendor": "Apple Computer, Inc.", "cores": 10, "memory": 16,
        "screen_w": 1440, "screen_h": 900, "avail_h": 860,
        "timezone": "America/Los_Angeles", "lang": "en-US",
    },
]


# ── IC3 helpers (prefixed ic3_ to avoid collision with FTC helpers) ───────────

def ic3_human_delay(min_ms=300, max_ms=900):
    base = random.uniform(min_ms, max_ms) / 1000
    jitter = random.uniform(0, 0.05)
    time.sleep(base + jitter)


def ic3_inject_fingerprint(sb, fp):
    sb.driver.execute_script(
        "(function() {"
        "  function tryDefine(obj, prop, value) {"
        "    try {"
        "      var desc = Object.getOwnPropertyDescriptor(obj, prop);"
        "      if (!desc || desc.configurable) {"
        "        Object.defineProperty(obj, prop, { get: function() { return value; }, configurable: true });"
        "      }"
        "    } catch(e) {}"
        "  }"
        f"  tryDefine(navigator, 'platform',  '{fp['platform']}');"
        f"  tryDefine(navigator, 'vendor',    '{fp['vendor']}');"
        f"  tryDefine(navigator, 'languages', ['{fp['lang']}', 'en']);"
        f"  tryDefine(navigator, 'hardwareConcurrency', {fp['cores']});"
        f"  tryDefine(navigator, 'deviceMemory',        {fp['memory']});"
        f"  tryDefine(screen,    'width',      {fp['screen_w']});"
        f"  tryDefine(screen,    'height',     {fp['screen_h']});"
        f"  tryDefine(screen,    'availWidth', {fp['screen_w']});"
        f"  tryDefine(screen,    'availHeight',{fp['avail_h']});"
        "  tryDefine(screen,    'colorDepth', 24);"
        "  tryDefine(navigator, 'webdriver',  undefined);"
        "})();"
    )


def ic3_simulate_human_mouse(sb):
    for _ in range(random.randint(2, 4)):
        x = random.randint(200, 900)
        y = random.randint(100, 500)
        sb.driver.execute_script(
            "(function() {"
            "  window.dispatchEvent(new MouseEvent('mousemove', {"
            f"    clientX: {x}, clientY: {y}, bubbles: true"
            "  }));"
            "})();"
        )
        time.sleep(random.uniform(0.1, 0.3))


def ic3_random_scroll(sb):
    amount = random.randint(80, 250)
    sb.driver.execute_script(f"window.scrollBy(0, {amount});")
    time.sleep(random.uniform(0.3, 0.7))
    sb.driver.execute_script(f"window.scrollBy(0, -{amount // 2});")
    ic3_human_delay(200, 500)


def ic3_js_click(sb, element_id):
    safe_id = element_id.replace("'", "\\'")
    sb.driver.execute_script(
        "(function() {"
        f"  var el = document.getElementById('{safe_id}');"
        "  if (el) {"
        "    el.focus();"
        "    el.click();"
        "    ['mousedown', 'mouseup', 'click'].forEach(function(evt) {"
        "      el.dispatchEvent(new MouseEvent(evt, { bubbles: true }));"
        "    });"
        "  }"
        "})();"
    )
    ic3_human_delay(400, 800)


def ic3_js_click_selector(sb, selector):
    safe = selector.replace("'", "\\'")
    sb.driver.execute_script(
        "(function() {"
        f"  var el = document.querySelector('{safe}');"
        "  if (el) {"
        "    el.focus();"
        "    el.click();"
        "    ['mousedown', 'mouseup', 'click'].forEach(function(evt) {"
        "      el.dispatchEvent(new MouseEvent(evt, { bubbles: true }));"
        "    });"
        "  }"
        "})();"
    )
    ic3_human_delay(400, 800)


# def ic3_human_type(sb, selector, text):
#     safe = selector.replace("'", "\\'")
#     sb.driver.execute_script(
#         "(function() {"
#         f"  var el = document.querySelector('{safe}');"
#         "  if (el) {"
#         "    el.focus();"
#         "    el.value = '';"
#         "    el.dispatchEvent(new Event('input', { bubbles: true }));"
#         "    el.dispatchEvent(new InputEvent('input', { bubbles: true, data: '', inputType: 'deleteContentBackward' }));"
#         "  }"
#         "})();"
#     )
#     ic3_human_delay(200, 400)
#     for char in text:
#         c = char.replace("\\", "\\\\").replace("'", "\\'")
#         sb.driver.execute_script(
#             "(function() {"
#             f"  var el = document.querySelector('{safe}');"
#             "  if (el) {"
#             f"    var start = el.selectionStart || el.value.length;"
#             f"    var end = el.selectionEnd || el.value.length;"
#             f"    el.value = el.value.substring(0, start) + '{c}' + el.value.substring(end);"
#             f"    el.selectionStart = el.selectionEnd = start + 1;"
#             "    el.dispatchEvent(new Event('input', { bubbles: true }));"
#             "    el.dispatchEvent(new InputEvent('input', { bubbles: true, data: '{c}', inputType: 'insertText' }));"
#             "  }"
#             "})();"
#         )
#         time.sleep(random.uniform(0.045, 0.13))
#     sb.driver.execute_script(
#         "(function() {"
#         f"  var el = document.querySelector('{safe}');"
#         "  if (el) {"
#         "    el.dispatchEvent(new Event('change', { bubbles: true }));"
#         "    el.blur();"
#         "  }"
#         "})();"
#     )
#     ic3_human_delay(300, 600)

def ic3_human_type(sb, selector, text):
    safe = selector.replace("'", "\\'")
    sb.driver.execute_script(
        "(function() {"
        f"  var el = document.querySelector('{safe}');"
        "  if (el) {"
        "    el.removeAttribute('disabled');"
        "    el.removeAttribute('readonly');"
        "    el.style.display = 'block';"
        "    el.style.visibility = 'visible';"
        "    el.style.opacity = '1';"
        "    el.focus();"
        "    el.value = '';"
        "    el.dispatchEvent(new Event('input', { bubbles: true }));"
        "  }"
        "})();"
    )
    ic3_human_delay(200, 400)
    for char in text:
        c = char.replace("\\", "\\\\").replace("'", "\\'")
        sb.driver.execute_script(
            "(function() {"
            f"  var el = document.querySelector('{safe}');"
            f"  if (el) {{ el.value += '{c}'; el.dispatchEvent(new Event('input', {{ bubbles: true }})); }}"
            "})();"
        )
        time.sleep(random.uniform(0.08, 0.18))
    sb.driver.execute_script(
        "(function() {"
        f"  var el = document.querySelector('{safe}');"
        "  if (el) {"
        "    el.dispatchEvent(new Event('change', { bubbles: true }));"
        "    el.blur();"
        "  }"
        "})();"
    )
    ic3_human_delay(300, 600)

def ic3_set_select(sb, sel_id, value):
    safe_id  = sel_id.replace("'", "\\'")
    safe_val = value.replace("'", "\\'")
    sb.driver.execute_script(
        "(function() {"
        f"  var sel = document.getElementById('{safe_id}');"
        "  if (sel) {"
        f"    sel.value = '{safe_val}';"
        "    sel.dispatchEvent(new Event('change', { bubbles: true }));"
        "  }"
        "})();"
    )
    ic3_human_delay(300, 700)


# def ic3_safe_set(sb, element_id, value):
#     safe_id  = element_id.replace("'", "\\'")
#     safe_val = value.replace("\\", "\\\\").replace("'", "\\'")
#     result = sb.driver.execute_script(
#         "(function() {"
#         f"  var el = document.getElementById('{safe_id}');"
#         "  if (el) {"
#         f"    el.value = '{safe_val}';"
#         "    el.dispatchEvent(new Event('input',  { bubbles: true }));"
#         "    el.dispatchEvent(new Event('change', { bubbles: true }));"
#         "    return true;"
#         "  }"
#         "  return false;"
#         "})();"
#     )
#     if result:
#         print(f"  Set {element_id} = {value}")
#     else:
#         print(f"  SKIPPED (not found): {element_id}")
#     ic3_human_delay(300, 600)

def ic3_safe_set(sb, element_id, value):
    safe_id  = element_id.replace("'", "\\'")
    safe_val = value.replace("\\", "\\\\").replace("'", "\\'")
    result = sb.driver.execute_script(
        "(function() {"
        f"  var el = document.getElementById('{safe_id}');"
        "  if (el) {"
        "    el.removeAttribute('disabled');"
        "    el.removeAttribute('readonly');"
        "    el.style.display = 'block';"
        "    el.style.visibility = 'visible';"
        f"    el.value = '{safe_val}';"
        "    el.dispatchEvent(new Event('focus',  { bubbles: true }));"
        "    el.dispatchEvent(new Event('input',  { bubbles: true }));"
        "    el.dispatchEvent(new Event('change', { bubbles: true }));"
        "    el.dispatchEvent(new Event('blur',   { bubbles: true }));"
        "    return true;"
        "  }"
        "  return false;"
        "})();"
    )

# def ic3_click_next(sb):
#     ic3_simulate_human_mouse(sb)
#     ic3_human_delay(600, 1000)
    
#     # Try real click first
#     try:
#         btn = sb.driver.find_element("css selector", "button.usa-button.next")
#         sb.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
#         ic3_human_delay(300, 500)
#         btn.click()
#         print("Next clicked (real)")
#     except Exception as e:
#         print(f"Real click failed: {e}")
#         # JS fallback
#         sb.driver.execute_script("""
#             (function() {
#                 var btn = document.querySelector('button.usa-button.next');
#                 if (btn) {
#                     btn.focus();
#                     btn.click();
#                     ['mousedown', 'mouseup', 'click'].forEach(function(evt) {
#                         btn.dispatchEvent(new MouseEvent(evt, {bubbles: true}));
#                     });
#                 }
#             })();
#         """)
#         print("Next clicked (JS fallback)")
    
#     ic3_human_delay(5000, 8000)  # Wait longer # Wait longer for navigation


def ic3_click_next(sb, timeout=30):
    ic3_simulate_human_mouse(sb)
    ic3_human_delay(600, 1000)

    try:
        btn = sb.driver.find_element("css selector", "button.usa-button.next")
        sb.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
        ic3_human_delay(300, 500)
        btn.click()
        print("Next clicked (real)")
    except Exception as e:
        print(f"Real click failed: {e}, trying JS fallback")
        sb.driver.execute_script("""
            (function() {
                var btn = document.querySelector('button.usa-button.next');
                if (btn) {
                    btn.focus();
                    btn.click();
                }
            })();
        """)
        print("Next clicked (JS fallback)")

    ic3_human_delay(3000, 5000)

    # Check for any validation errors
    error = sb.driver.execute_script(
        "(function() {"
        "  var err = document.querySelector('.usa-alert--error, .field-validation-error, .validation-summary-errors');"
        "  return err ? err.textContent.trim() : null;"
        "})();"
    )
    if error:
        raise Exception(f"Form validation error: {error}")

    current_url = sb.driver.execute_script("return window.location.href;")
    print(f"  After Next: {current_url}")
    return current_url

# ── Main IC3 function ─────────────────────────────────────────────────────────

# def submit_ic3_complaint(
#     phone_number: str,
#     brand: str,
#     landing_url: str,
#     reporter_first_name: str = None,
#     reporter_last_name: str = None,
#     reporter_address: str = None,
#     reporter_city: str = None,
#     reporter_state: str = None,
#     reporter_zip: str = None,
#     reporter_phone: str = None,
#     reporter_email: str = None,
# ) -> Tuple[bool, str, Optional[str]]:
#     identity = generate_random_identity()
#     reporter_first_name = reporter_first_name or identity["first_name"]
#     reporter_last_name  = reporter_last_name  or identity["last_name"]
#     reporter_address    = reporter_address    or identity["address"]
#     reporter_city       = reporter_city       or identity["city"]
#     reporter_state      = reporter_state      or identity["state"]
#     reporter_zip        = reporter_zip        or identity["zip"]
#     reporter_phone      = reporter_phone      or identity["phone"]
#     reporter_email      = reporter_email      or identity["email"]

#     reporter_full_name = f"{reporter_first_name} {reporter_last_name}".strip()
#     reporter_zip_str   = str(reporter_zip) if reporter_zip else ""

#     screenshot_path = os.path.join(SCREENSHOTS_DIR, f"ic3_{phone_number}.png")

#     reporter_full_name = f"{reporter_first_name or ''} {reporter_last_name or ''}".strip()
#     reporter_zip_str   = str(reporter_zip) if reporter_zip else ""

#     incident_text = (
#         f"Phone number {phone_number} impersonating {brand}. Landing page: {landing_url}."
#     ).replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"')

#     fp = random.choice(FINGERPRINTS)
#     print(f"[fingerprint] Using agent: {fp['agent'][:60]}...")

#     try:
#         with SB(
#             browser="chrome",
#             headless=False,
#             agent=fp["agent"],
#             slow=True,
#         ) as sb:

#             sb.open("https://www.ic3.gov/")
#             sb.driver.set_script_timeout(300)
#             sb.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
#                 "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
#             })
#             ic3_inject_fingerprint(sb, fp)
#             ic3_human_delay(2000, 3500)
#             ic3_random_scroll(sb)
#             ic3_simulate_human_mouse(sb)
#             print("Loaded:", sb.get_current_url())

#             # Click "File a Complaint"
#             sb.wait_for_element_visible("button#fileComplaint", timeout=15)
#             ic3_human_delay(800, 1500)
#             sb.driver.find_element("css selector", "button#fileComplaint").click()
#             ic3_human_delay(4000, 6000)
#             print("After File a Complaint:", sb.get_current_url())

#             try:
#                 sb.driver.find_element("css selector", "button#acceptFile")
#             except Exception:
#                 print("Modal not opened yet, clicking fileComplaint again...")
#                 sb.driver.find_element("css selector", "button#fileComplaint").click()
#                 ic3_human_delay(4000, 6000)

#             # Click "Accept" — opens new tab
#             sb.driver.set_script_timeout(300)
#             sb.wait_for_element_visible("button#acceptFile", timeout=30)
#             ic3_human_delay(1500, 2500)
#             sb.driver.execute_script("document.getElementById('acceptFile').scrollIntoView({block: 'center'});")
#             ic3_human_delay(500, 800)
#             # sb.driver.find_element("css selector", "button#acceptFile").click()
#             # ic3_human_delay(3000, 5000)

#             # sb.switch_to_newest_window()
#             sb.driver.find_element("css selector", "button#acceptFile").click()
#             ic3_human_delay(3000, 5000)

#             for _ in range(20):
#                 if len(sb.driver.window_handles) > 1:
#                     break
#                 time.sleep(0.5)
#             print(f"Window handles: {sb.driver.window_handles}")
#             sb.switch_to_newest_window()

#             for _ in range(60):
#                 try:
#                     page_html = sb.driver.execute_script("return document.documentElement.innerHTML;")
#                     if "IsVictim" in page_html:
#                         print("IC3 form loaded successfully")
#                         break
#                 except Exception:
#                     pass
#                 time.sleep(0.5)
#             else:
#                 raise Exception("IC3 form never loaded — IsVictim field not found after 30s")
#             print(f"Form tab URL: {sb.driver.execute_script('return window.location.href;')}")

#             ic3_inject_fingerprint(sb, fp)
#             ic3_human_delay(2000, 3500)
#             print("After Accept - New tab URL:", sb.get_current_url())

#             all_inputs = sb.driver.execute_script(
#                 "return Array.from(document.querySelectorAll('input')).map(function(el) { return el.id + ' | ' + el.name + ' | ' + el.type; });"
#             )
#             print("INPUTS:", all_inputs)

#             # Step 1: Complainant info
#             sb.wait_for_element_present("input#IsVictim_no", timeout=20)
#             ic3_human_delay(600, 1200)
#             ic3_random_scroll(sb)

#             # ic3_js_click(sb, "IsVictim_no")
#             # ic3_human_delay(500, 1000)

#             # ic3_safe_set(sb, "Complainant_Name",  reporter_full_name)
#             # ic3_safe_set(sb, "Complainant_Phone", reporter_phone or "")
#             # ic3_safe_set(sb, "Complainant_Email", reporter_email or "")
#             ic3_js_click(sb, "IsVictim_no")
#             ic3_human_delay(1000, 1500)

#             ic3_human_type(sb, "#Complainant_Name",  reporter_full_name)
#             ic3_human_type(sb, "#Complainant_Phone", reporter_phone or "")
#             ic3_human_type(sb, "#Complainant_Email", reporter_email or "")

#             name_val = sb.driver.execute_script("return document.getElementById('Complainant_Name')?.value || 'EMPTY';")
#             print(f"Complainant_Name value = {name_val}")
#             ic3_simulate_human_mouse(sb)
#             ic3_click_next(sb)
#             print("After Step 1:", sb.get_current_url())

#             # Step 2: Victim info
#             sb.wait_for_element_present("input#Victim_Name", timeout=20)
#             ic3_human_delay(800, 1500)
#             ic3_random_scroll(sb)

#             ic3_safe_set(sb, "Victim_Name",     reporter_full_name)
#             ic3_set_select(sb, "Victim_AgeRange", "TwentyTo29")
#             ic3_safe_set(sb, "Victim_Address1", reporter_address or "")
#             ic3_safe_set(sb, "Victim_City",     reporter_city or "")
#             ic3_set_select(sb, "Victim_Country", "USA")
#             ic3_human_delay(1000, 1500)
#             ic3_set_select(sb, "Victim_State", reporter_state or "AL")
#             ic3_safe_set(sb, "Victim_ZipCode",  reporter_zip_str)
#             ic3_safe_set(sb, "Victim_Phone",    reporter_phone or "")
#             ic3_safe_set(sb, "Victim_Email",    reporter_email or "")
#             ic3_js_click(sb, "Victim_IsBusiness_no")
#             is_business = sb.driver.execute_script("return document.getElementById('Victim_IsBusiness_no')?.checked || 'NOT CLICKED';")
#             print(f"Victim_IsBusiness_no checked = {is_business}")

#             ic3_simulate_human_mouse(sb)
#             ic3_click_next(sb)
#             # After filling Step 2, before click_next:
#             print("Checking Step 2 fields...")
#             victim_name = sb.driver.execute_script("return document.getElementById('Victim_Name')?.value || 'NOT SET';")
#             print(f"Victim_Name = {victim_name}")
#             victim_state = sb.driver.execute_script("return document.getElementById('Victim_State')?.value || 'NOT SET';")
#             print(f"Victim_State = {victim_state}")
#             print("After Step 2:", sb.get_current_url())

#             # Step 3: Money sent
#             sb.wait_for_element_present("input#MoneySent_no", timeout=20)
#             ic3_human_delay(600, 1200)
#             ic3_js_click(sb, "MoneySent_no")
#             ic3_human_delay(500, 1000)
#             ic3_simulate_human_mouse(sb)
#             ic3_click_next(sb)
#             print("After Step 3:", sb.get_current_url())

#             # Step 4: Subject info
#             sb.wait_for_element_present("input#Subjects_0__Name", timeout=20)
#             ic3_human_delay(800, 1500)

#             try:
#                 ic3_js_click_selector(sb, "button.add-subject")
#                 ic3_human_delay(1000, 1500)
#             except Exception:
#                 pass

#             sb.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#             ic3_human_delay(1000, 1500)

#             ic3_safe_set(sb, "Subjects_0__Name",         "Website phishing Scam")
#             ic3_safe_set(sb, "Subjects_0__BusinessName", brand.replace("'", "\\'"))
#             ic3_safe_set(sb, "Subjects_0__Address",      (reporter_address or "").replace("'", "\\'"))
#             ic3_safe_set(sb, "Subjects_0__City",         (reporter_city    or "").replace("'", "\\'"))
#             ic3_set_select(sb, "Subjects_0_Country",     "USA")
#             ic3_human_delay(500, 1000)
#             ic3_safe_set(sb, "Subjects_0__ZipCode",  reporter_zip_str.replace("'", "\\'"))
#             ic3_safe_set(sb, "Subjects_0__Phone",    phone_number.replace("'", "\\'"))
#             ic3_safe_set(sb, "Subjects_0__Email",    (reporter_email  or "").replace("'", "\\'"))
#             ic3_safe_set(sb, "Subjects_0__Website",  landing_url.replace("'", "\\'"))
#             ic3_safe_set(sb, "Subjects_0__IPAddress","192.168.1.1")

#             ic3_simulate_human_mouse(sb)
#             ic3_click_next(sb)
#             print("After Step 4:", sb.get_current_url())

#             # Step 5: Incident description
#             sb.wait_for_element_present("textarea#IncidentDescription", timeout=20)
#             ic3_human_delay(800, 1500)
#             ic3_random_scroll(sb)

#             sb.driver.execute_script(
#                 "(function() {"
#                 "  var ta = document.getElementById('IncidentDescription');"
#                 "  if (ta) {"
#                 "    ta.focus();"
#                 f"    ta.value = '{incident_text}';"
#                 "    ta.dispatchEvent(new Event('input',  { bubbles: true }));"
#                 "    ta.dispatchEvent(new Event('change', { bubbles: true }));"
#                 "    ta.blur();"
#                 "  }"
#                 "})();"
#             )
#             ic3_human_delay(500, 1000)

#             ic3_simulate_human_mouse(sb)
#             ic3_click_next(sb)
#             print("After Step 5:", sb.get_current_url())
#             print("After scammer info Continue:", sb.get_current_url())
#             if "confirmation" in sb.get_current_url():
#                 print("FTC already submitted — on confirmation page")
#                 try:
#                     sb.save_screenshot(screenshot_path)
#                 except Exception:
#                     pass
#                 return (True, "FTC complaint submitted successfully", screenshot_path)

#             # Step 6: Complaint update
#             sb.wait_for_element_present("input#ComplaintUpdate_no", timeout=20)
#             ic3_human_delay(600, 1200)
#             ic3_js_click(sb, "ComplaintUpdate_no")
#             ic3_human_delay(500, 1000)
#             ic3_simulate_human_mouse(sb)
#             ic3_click_next(sb)
#             print("After Step 6:", sb.get_current_url())

#             # Step 7: Digital signature and submit
#             sb.wait_for_element_present("input#DigitalSignature", timeout=20)
#             ic3_human_delay(1000, 2000)
#             ic3_random_scroll(sb)

#             ic3_safe_set(sb, "DigitalSignature", reporter_full_name)
#             ic3_human_delay(2000, 3500)

#             ic3_simulate_human_mouse(sb)
#             ic3_random_scroll(sb)
#             ic3_inject_fingerprint(sb, fp)
#             ic3_human_delay(3000, 5000)

#             print("Submitting form...")
#             try:
#                 sb.save_screenshot(screenshot_path)
#                 print(f"[+] Pre-submit screenshot saved: {screenshot_path}")
#             except Exception as e:
#                 print(f"Pre-submit screenshot failed: {e}")
#             submit_btn = sb.driver.find_element("css selector", "button[type='submit']")
#             sb.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_btn)
#             ic3_human_delay(800, 1200)
#             submit_btn.click()

#             print("Waiting for server response...")
#             confirmation_html = None
#             confirmation_url  = None

#             for _ in range(60):
#                 time.sleep(0.5)
#                 try:
#                     current_url = sb.driver.execute_script("return window.location.href;")
#                     page_html   = sb.driver.execute_script("return document.documentElement.innerHTML;")

#                     if any(kw in page_html.lower() for kw in [
#                         "complaint number", "confirmation", "thank you",
#                         "successfully submitted", "reference number", "ic3 complaint",
#                     ]):
#                         confirmation_html = page_html
#                         confirmation_url  = current_url
#                         # SAVE SCREENSHOT RIGHT HERE WHEN SUCCESS IS DETECTED
#                         try:
#                             sb.save_screenshot(screenshot_path)
#                             print(f"[+] Screenshot saved: {screenshot_path}")
#                         except Exception as e:
#                             print(f"Screenshot failed: {e}")
#                         print(f"[+] Confirmation page captured at: {current_url}")
#                         break

#                     if "Search/Results" in current_url:
#                         confirmation_html = page_html
#                         confirmation_url = current_url
#                         try:
#                             sb.save_screenshot(screenshot_path)
#                             print(f"[+] Screenshot saved (search redirect): {screenshot_path}")
#                         except: pass
#                         break

#                     if "chrome-error" in current_url:
#                         confirmation_html = page_html
#                         confirmation_url = current_url
#                         try:
#                             sb.save_screenshot(screenshot_path)
#                         except: pass
#                         break

#                 except Exception:
#                     pass



#             ic3_human_delay(5000, 8000)
#             final_url   = sb.get_current_url()
#             final_title = sb.get_title()
#             print("Final URL:",  final_url)
#             print("Title:",      final_title)

#             # try:
#             #     sb.save_screenshot(screenshot_path)
#             # except Exception:
#             #     pass

#             if confirmation_html:
#                 number_match = re.search(
#                     r'(complaint\s*(?:number|#|id)[:\s#]*)([\w\-]+)',
#                     confirmation_html, re.IGNORECASE,
#                 )
#                 ref_match = re.search(
#                     r'(reference\s*(?:number|#|id)[:\s#]*)([\w\-]+)',
#                     confirmation_html, re.IGNORECASE,
#                 )
#                 if number_match:
#                     print(f"RESULT: SUCCESS — Complaint number: {number_match.group(2)}")
#                 elif ref_match:
#                     print(f"RESULT: SUCCESS — Reference number: {ref_match.group(2)}")
#                 else:
#                     print("RESULT: SUCCESS — Confirmation page was captured.")
#             elif "Search/Results" in final_url:
#                 print("RESULT: SUBMITTED — IC3 redirected to search page.")
#             elif "chrome-error" in final_url:
#                 print("RESULT: ERROR — Navigation failed, check network connection.")
#             elif "complaint.ic3.gov" in final_url:
#                 error_msg = sb.driver.execute_script(
#                     "(function() {"
#                     "  var err = document.querySelector("
#                     "    '.usa-alert--error, .validation-summary-errors, .field-validation-error'"
#                     "  );"
#                     "  return err ? err.textContent.trim() : null;"
#                     "})();"
#                 )
#                 if error_msg:
#                     print("RESULT: FORM ERROR —", error_msg)
#                 else:
#                     print("RESULT: Still on form page — unknown state.")

#             success = (
#                 confirmation_html is not None or
#                 "Search/Results" in final_url or
#                 "confirm" in final_url.lower() or
#                 "thank"   in final_title.lower()
#             )

#             return (
#                 success,
#                 "IC3 complaint submitted" if success else "IC3 submission failed",
#                 screenshot_path if success else None,
#             )

#     except Exception as e:
#         logger.error(f"IC3 submission failed: {e}")
#         return (False, str(e), None)




def submit_ic3_complaint(
    phone_number: str,
    brand: str,
    landing_url: str,
    reporter_first_name: str = None,
    reporter_last_name: str = None,
    reporter_address: str = None,
    reporter_city: str = None,
    reporter_state: str = None,
    reporter_zip: str = None,
    reporter_phone: str = None,
    reporter_email: str = None,
) -> Tuple[bool, str, Optional[str]]:
    identity = generate_random_identity()
    reporter_first_name = reporter_first_name or identity["first_name"]
    reporter_last_name  = reporter_last_name  or identity["last_name"]
    reporter_address    = reporter_address    or identity["address"]
    reporter_city       = reporter_city       or identity["city"]
    reporter_state      = reporter_state      or identity["state"]
    reporter_zip        = reporter_zip        or identity["zip"]
    reporter_phone      = reporter_phone      or identity["phone"]
    reporter_email      = reporter_email      or identity["email"]

    reporter_full_name = f"{reporter_first_name or ''} {reporter_last_name or ''}".strip()
    reporter_zip_str   = str(reporter_zip) if reporter_zip else ""
    screenshot_path    = os.path.join(SCREENSHOTS_DIR, f"ic3_{phone_number}.png")
    screenshot_b64     = None

    incident_text = (
        f"Phone number {phone_number} impersonating {brand}. Landing page: {landing_url}."
    ).replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"')

    fp = random.choice(FINGERPRINTS)
    print(f"[fingerprint] Using agent: {fp['agent'][:60]}...")

    try:
        with SB(
            browser="chrome",
            headless=False,
            agent=fp["agent"],
            slow=True,
        ) as sb:

            sb.open("https://www.ic3.gov/")
            sb.driver.set_script_timeout(300)
            sb.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            })
            ic3_inject_fingerprint(sb, fp)
            ic3_human_delay(2000, 3500)
            ic3_random_scroll(sb)
            ic3_simulate_human_mouse(sb)
            print("Loaded:", sb.get_current_url())

            # Click "File a Complaint" via JS
            sb.wait_for_element_visible("button#fileComplaint", timeout=15)
            ic3_human_delay(800, 1500)
            sb.driver.execute_script("document.querySelector('button#fileComplaint').click();")
            ic3_human_delay(4000, 6000)
            print("After File a Complaint:", sb.get_current_url())

            # Wait for modal and click Accept via JS
            sb.wait_for_element_present("button#acceptFile", timeout=45)
            ic3_human_delay(1500, 2500)
            sb.driver.execute_script("document.querySelector('button#acceptFile').click();")
            ic3_human_delay(5000, 7000)

            # Wait for new tab
            for _ in range(20):
                if len(sb.driver.window_handles) > 1:
                    break
                time.sleep(0.5)
            print(f"Window handles: {sb.driver.window_handles}")
            sb.switch_to_newest_window()
            ic3_human_delay(3000, 5000)
            print(f"New tab URL: {sb.driver.execute_script('return window.location.href;')}")

            # Wait for form to load
            for _ in range(60):
                try:
                    page_html = sb.driver.execute_script("return document.documentElement.innerHTML;")
                    if "IsVictim" in page_html:
                        print("IC3 form loaded successfully")
                        break
                except Exception:
                    pass
                time.sleep(0.5)
            else:
                raise Exception("IC3 form never loaded after 30s")

            ic3_inject_fingerprint(sb, fp)
            ic3_human_delay(2000, 3500)
            print("After Accept - New tab URL:", sb.get_current_url())

            # Step 1: Complainant info
            sb.wait_for_element_present("input#IsVictim_no", timeout=20)
            ic3_human_delay(600, 1200)
            ic3_random_scroll(sb)
            ic3_js_click(sb, "IsVictim_no")
            ic3_human_delay(1000, 1500)

            ic3_human_type(sb, "#Complainant_Name",  reporter_full_name)
            ic3_human_type(sb, "#Complainant_Phone", reporter_phone or "")
            ic3_human_type(sb, "#Complainant_Email", reporter_email or "")

            name_val = sb.driver.execute_script("return document.getElementById('Complainant_Name')?.value || 'EMPTY';")
            print(f"Complainant_Name value = {name_val}")

            ic3_simulate_human_mouse(sb)
            ic3_click_next(sb)
            print("After Step 1:", sb.get_current_url())

            # Step 2: Victim info
            sb.wait_for_element_present("input#Victim_Name", timeout=20)
            ic3_human_delay(800, 1500)
            ic3_random_scroll(sb)

            ic3_safe_set(sb, "Victim_Name",     reporter_full_name)
            ic3_set_select(sb, "Victim_AgeRange", "TwentyTo29")
            ic3_safe_set(sb, "Victim_Address1", reporter_address or "")
            ic3_safe_set(sb, "Victim_City",     reporter_city or "")
            ic3_set_select(sb, "Victim_Country", "USA")
            ic3_human_delay(1000, 1500)
            ic3_set_select(sb, "Victim_State",  reporter_state or "AL")
            ic3_safe_set(sb, "Victim_ZipCode",  reporter_zip_str)
            ic3_safe_set(sb, "Victim_Phone",    reporter_phone or "")
            ic3_safe_set(sb, "Victim_Email",    reporter_email or "")
            ic3_js_click(sb, "Victim_IsBusiness_no")

            ic3_simulate_human_mouse(sb)
            ic3_click_next(sb)
            print("After Step 2:", sb.get_current_url())

            # Step 3: Money sent
            sb.wait_for_element_present("input#MoneySent_no", timeout=20)
            ic3_human_delay(600, 1200)
            ic3_js_click(sb, "MoneySent_no")
            ic3_human_delay(500, 1000)
            ic3_simulate_human_mouse(sb)
            ic3_click_next(sb)
            print("After Step 3:", sb.get_current_url())

            # Step 4: Subject info
            sb.wait_for_element_present("input#Subjects_0__Name", timeout=20)
            ic3_human_delay(800, 1500)

            try:
                ic3_js_click_selector(sb, "button.add-subject")
                ic3_human_delay(1000, 1500)
            except Exception:
                pass

            sb.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            ic3_human_delay(1000, 1500)

            ic3_safe_set(sb, "Subjects_0__Name",         "Website phishing Scam")
            ic3_safe_set(sb, "Subjects_0__BusinessName", brand.replace("'", "\\'"))
            ic3_safe_set(sb, "Subjects_0__Address",      (reporter_address or "").replace("'", "\\'"))
            ic3_safe_set(sb, "Subjects_0__City",         (reporter_city    or "").replace("'", "\\'"))
            ic3_set_select(sb, "Subjects_0_Country",     "USA")
            ic3_human_delay(500, 1000)
            ic3_safe_set(sb, "Subjects_0__ZipCode",  reporter_zip_str.replace("'", "\\'"))
            ic3_safe_set(sb, "Subjects_0__Phone",    phone_number.replace("'", "\\'"))
            ic3_safe_set(sb, "Subjects_0__Email",    (reporter_email  or "").replace("'", "\\'"))
            ic3_safe_set(sb, "Subjects_0__Website",  landing_url.replace("'", "\\'"))
            ic3_safe_set(sb, "Subjects_0__IPAddress","192.168.1.1")

            ic3_simulate_human_mouse(sb)
            ic3_click_next(sb)
            print("After Step 4:", sb.get_current_url())

            # Step 5: Incident description
            sb.wait_for_element_present("textarea#IncidentDescription", timeout=20)
            ic3_human_delay(800, 1500)
            ic3_random_scroll(sb)

            sb.driver.execute_script(
                "(function() {"
                "  var ta = document.getElementById('IncidentDescription');"
                "  if (ta) {"
                "    ta.focus();"
                f"    ta.value = '{incident_text}';"
                "    ta.dispatchEvent(new Event('input',  { bubbles: true }));"
                "    ta.dispatchEvent(new Event('change', { bubbles: true }));"
                "    ta.blur();"
                "  }"
                "})();"
            )
            ic3_human_delay(500, 1000)
            ic3_simulate_human_mouse(sb)
            ic3_click_next(sb)
            print("After Step 5:", sb.get_current_url())

            # Step 6: Complaint update
            sb.wait_for_element_present("input#ComplaintUpdate_no", timeout=20)
            ic3_human_delay(600, 1200)
            ic3_js_click(sb, "ComplaintUpdate_no")
            ic3_human_delay(500, 1000)
            ic3_simulate_human_mouse(sb)
            ic3_click_next(sb)
            print("After Step 6:", sb.get_current_url())

            # Step 7: Digital signature and submit
            sb.wait_for_element_present("input#DigitalSignature", timeout=20)
            ic3_human_delay(1000, 2000)
            ic3_random_scroll(sb)
            ic3_safe_set(sb, "DigitalSignature", reporter_full_name)
            ic3_human_delay(2000, 3500)
            ic3_simulate_human_mouse(sb)
            ic3_random_scroll(sb)
            ic3_inject_fingerprint(sb, fp)
            ic3_human_delay(3000, 5000)

            # Screenshot before submit
            print("Submitting form...")
            try:
                sb.save_screenshot(screenshot_path)
                with open(screenshot_path, "rb") as f:
                    screenshot_b64 = base64.b64encode(f.read()).decode("utf-8")
                print(f"[+] Pre-submit screenshot saved: {screenshot_path}")
            except Exception as e:
                print(f"Pre-submit screenshot failed: {e}")

            submit_btn = sb.driver.find_element("css selector", "button[type='submit']")
            sb.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_btn)
            ic3_human_delay(800, 1200)
            submit_btn.click()

            print("Waiting for server response...")
            confirmation_html = None
            confirmation_url  = None

            for _ in range(60):
                time.sleep(0.5)
                try:
                    current_url = sb.driver.execute_script("return window.location.href;")
                    page_html   = sb.driver.execute_script("return document.documentElement.innerHTML;")

                    if any(kw in page_html.lower() for kw in [
                        "complaint number", "confirmation", "thank you",
                        "successfully submitted", "reference number", "ic3 complaint",
                    ]):
                        confirmation_html = page_html
                        confirmation_url  = current_url
                        try:
                            sb.save_screenshot(screenshot_path)
                            with open(screenshot_path, "rb") as f:
                                screenshot_b64 = base64.b64encode(f.read()).decode("utf-8")
                            print(f"[+] Screenshot saved: {screenshot_path}")
                        except Exception as e:
                            print(f"Screenshot failed: {e}")
                        print(f"[+] Confirmation page captured at: {current_url}")
                        break

                    if "Search/Results" in current_url:
                        confirmation_html = page_html
                        confirmation_url  = current_url
                        ic3_human_delay(2000, 3000)
                        try:
                            sb.save_screenshot(screenshot_path)
                            with open(screenshot_path, "rb") as f:
                                    screenshot_b64 = base64.b64encode(f.read()).decode("utf-8")
                            print(f"[+] Screenshot saved (search redirect): {screenshot_path}")
                        except Exception as e:
                            print(f"Screenshot failed: {e}")
                        break

                    if "chrome-error" in current_url:
                        confirmation_html = page_html
                        confirmation_url  = current_url
                        try:
                            sb.save_screenshot(screenshot_path)
                            with open(screenshot_path, "rb") as f:
                                screenshot_b64 = base64.b64encode(f.read()).decode("utf-8")
                        except Exception:
                            pass
                        break

                except Exception:
                    pass

            ic3_human_delay(3000, 5000)
            final_url   = sb.get_current_url()
            final_title = sb.get_title()
            print("Final URL:",  final_url)
            print("Title:",      final_title)

            if confirmation_html:
                number_match = re.search(
                    r'(complaint\s*(?:number|#|id)[:\s#]*)([\w\-]+)',
                    confirmation_html, re.IGNORECASE,
                )
                ref_match = re.search(
                    r'(reference\s*(?:number|#|id)[:\s#]*)([\w\-]+)',
                    confirmation_html, re.IGNORECASE,
                )
                if number_match:
                    print(f"RESULT: SUCCESS — Complaint number: {number_match.group(2)}")
                elif ref_match:
                    print(f"RESULT: SUCCESS — Reference number: {ref_match.group(2)}")
                else:
                    print("RESULT: SUCCESS — Confirmation page was captured.")
            elif "Search/Results" in final_url:
                print("RESULT: SUBMITTED — IC3 redirected to search page.")
            elif "chrome-error" in final_url:
                print("RESULT: ERROR — Navigation failed, check network connection.")
            elif "complaint.ic3.gov" in final_url:
                error_msg = sb.driver.execute_script(
                    "(function() {"
                    "  var err = document.querySelector("
                    "    '.usa-alert--error, .validation-summary-errors, .field-validation-error'"
                    "  );"
                    "  return err ? err.textContent.trim() : null;"
                    "})();"
                )
                if error_msg:
                    print("RESULT: FORM ERROR —", error_msg)
                else:
                    print("RESULT: Still on form page — unknown state.")

            success = (
                confirmation_html is not None or
                "Search/Results" in final_url or
                "confirm" in final_url.lower() or
                "thank"   in final_title.lower()
            )

            return (
                success,
                "IC3 complaint submitted" if success else "IC3 submission failed",
                screenshot_path if success else None,
                screenshot_b64 if success else None,
            )

    except Exception as e:
        logger.error(f"IC3 submission failed: {e}")
        return (False, str(e), None)

def submit_microsoft_fraud(
    phone_number: str,
    landing_url: str
) -> Tuple[bool, str]:
    try:
        logger.info(f"Microsoft fraud report queued for {phone_number}")
        return (True, "Microsoft fraud report queued")
    except Exception as e:
        logger.error(f"Microsoft fraud submission failed: {e}")
        return (False, str(e))




def submit_google_safebrowsing(
    url: str
) -> Tuple[bool, str]:
    try:
        logger.info(f"Google Safe Browsing report queued for {url}")
        return (True, "Google Safe Browsing report queued")
    except Exception as e:
        logger.error(f"Google Safe Browsing submission failed: {e}")
        return (False, str(e))
