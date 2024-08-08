import json
import sys
from pymongo import MongoClient
from graphics_matplotlib import *
import pulp
from infusion_settings import *


def parse_json(input_json):
    # Parse the JSON input
    data = json.loads(input_json)

    # Extract variables from JSON
    uri = data.get('uri')
    date = data.get('date')
    patients = data.get('patients', [])
    nurses = data.get('nurses', [])
    chairs = data.get('chairs', [])
    settings = data.get('settings', {})

    # Define variables based on the JSON data
    num_nurses = len(nurses)
    num_chairs = settings.get('numberOfChairs')
    M = settings.get('patientNurseRatio')
    open_time = settings.get('openTime')
    close_time = settings.get('closeTime')
    break_start_time = settings.get('break_start_time')
    break_end_time = settings.get('break_end_time')
    break_duration = settings.get('break_duration')

    return uri, id, date, num_nurses, num_chairs, M, open_time, close_time, patients, nurses, chairs, break_start_time, break_end_time, break_duration


def create_schedule_json(date, patients, nurses, allocation, naive_allocation, num_chairs, open_time, close_time):
    chairs = []

    for chair in range(num_chairs):
        chairs.append({"chairId": chair, 'assignedPatients': []})

    for alloc in allocation:
        patients[alloc[0]]["actualStartTime"] = alloc[1]
        patients[alloc[0]]["actualEndTime"] = alloc[2]
        patients[alloc[0]]["assignedChair"] = alloc[3]
        patients[alloc[0]]["assignedNurse"] = alloc[4]
        nurses[alloc[4]]["assignedPatients"].append(alloc[0])
        chairs[alloc[3]]["assignedPatients"].append(alloc[0])

    optimized_utilization_data = []

    utilization = calculate_utilization(allocation, open_time, close_time)[1]

    time_range = range(open_time, close_time + 1, 10)

    for i, time in enumerate(time_range):
        optimized_utilization_data.append({"time": time, "patientCount": utilization[i]})

    naive_utilization_data = []

    utilization = calculate_utilization(naive_allocation, open_time, close_time)[1]

    for i, time in enumerate(time_range):
        naive_utilization_data.append({"time": time, "patientCount": utilization[i]})

    scheduled_utilization_data = []

    utilization = calculate_orig_schedule_utilization(patients, open_time, close_time)[1]

    for i, time in enumerate(time_range):
        scheduled_utilization_data.append({"time": time, "patientCount": utilization[i]})

    acuity_dict = {}

    for patient in patients:
        if str(patient["acuity"]) not in acuity_dict:
            acuity_dict[str(patient["acuity"])] = 0
        acuity_dict[str(patient["acuity"])] += 1

    data = {
        'date': date,
        'patients': patients,
        'nurses': nurses,
        'chairs': chairs,
        'uploadedAt': date,
        'scheduledUtilization': scheduled_utilization_data,
        'naiveUtilization': naive_utilization_data,
        'actualUtilization': optimized_utilization_data,
        'acuityMix': acuity_dict
    }

    return data


def create_roi_json(date, optimized_roi, unoptimized_roi):
    data = {
        'date': date,
        'unoptimized': unoptimized_roi,
        'optimized': optimized_roi
    }

    return data


def connect_to_mongo(uri):
    client = MongoClient(uri)
    return client


def upload_schedule(db, collection_name, schedule_data):
    collection = db[collection_name]

    # Assuming schedule_data has a 'date' field
    date = schedule_data['date']

    result = collection.update_one(
        {'date': date},  # Filter criteria
        {'$set': schedule_data},  # Data to update
        upsert=True  # Insert the document if it does not exist
    )

    return result


def upload_roi(db, collection_name, roi_json):
    collection = db[collection_name]

    # Assuming schedule_data has a 'date' field
    date = roi_json['date']

    result = collection.update_one(
        {'date': date},  # Filter criteria
        {'$set': roi_json},  # Data to update
        upsert=True  # Insert the document if it does not exist
    )

    return result


def main():
    prod = True
    if prod:
        if len(sys.argv) != 2:
            print("Usage: python infusion.py '<json_input>'")
            sys.exit(1)

        input_json = sys.argv[1]
    else:
        input_json = '{"uri":"mongodb+srv://MainLine:TheBigNurse@scheduleevents.xourcma.mongodb.net/Paoli?retryWrites=true&w=majority&appName=ScheduleEvents","date":"2024-05-28","patients":[{"patientId":0,"patientMRN":6740576476,"patientName":"John Smith","readyTime":770,"dueTime":1080,"actualStartTime":-1,"length":60,"acuity":2,"assignedChair":-1,"assignedNurse":-1},{"patientId":1,"patientMRN":8178012217,"patientName":"Emma Johnson","readyTime":920,"dueTime":1080,"actualStartTime":-1,"length":60,"acuity":3,"assignedChair":-1,"assignedNurse":-1},{"patientId":2,"patientMRN":3309061148,"patientName":"James Williams","readyTime":630,"dueTime":1080,"actualStartTime":-1,"length":60,"acuity":2,"assignedChair":-1,"assignedNurse":-1},{"patientId":3,"patientMRN":1998004609,"patientName":"Olivia Brown","readyTime":850,"dueTime":1080,"actualStartTime":-1,"length":60,"acuity":2,"assignedChair":-1,"assignedNurse":-1},{"patientId":4,"patientMRN":7650049569,"patientName":"William Jones","readyTime":810,"dueTime":1080,"actualStartTime":-1,"length":60,"acuity":2,"assignedChair":-1,"assignedNurse":-1},{"patientId":5,"patientMRN":7463043793,"patientName":"Ava Davis","readyTime":970,"dueTime":1080,"actualStartTime":-1,"length":60,"acuity":3,"assignedChair":-1,"assignedNurse":-1},{"patientId":6,"patientMRN":683826721,"patientName":"Noah Miller","readyTime":930,"dueTime":1080,"actualStartTime":-1,"length":60,"acuity":1,"assignedChair":-1,"assignedNurse":-1},{"patientId":7,"patientMRN":7967037465,"patientName":"Sophia Wilson","readyTime":690,"dueTime":1080,"actualStartTime":-1,"length":60,"acuity":1,"assignedChair":-1,"assignedNurse":-1},{"patientId":8,"patientMRN":1313080269,"patientName":"Liam Moore","readyTime":480,"dueTime":1080,"actualStartTime":-1,"length":60,"acuity":1,"assignedChair":-1,"assignedNurse":-1},{"patientId":9,"patientMRN":1691442502,"patientName":"Isabella Taylor","readyTime":960,"dueTime":1080,"actualStartTime":-1,"length":60,"acuity":3,"assignedChair":-1,"assignedNurse":-1},{"patientId":10,"patientMRN":8028191545,"patientName":"Mason Anderson","readyTime":1020,"dueTime":1080,"actualStartTime":-1,"length":60,"acuity":2,"assignedChair":-1,"assignedNurse":-1},{"patientId":11,"patientMRN":4156807847,"patientName":"Mia Thomas","readyTime":990,"dueTime":1080,"actualStartTime":-1,"length":60,"acuity":3,"assignedChair":-1,"assignedNurse":-1},{"patientId":12,"patientMRN":686178896,"patientName":"Ethan Jackson","readyTime":690,"dueTime":1080,"actualStartTime":-1,"length":60,"acuity":2,"assignedChair":-1,"assignedNurse":-1},{"patientId":13,"patientMRN":4572722401,"patientName":"Amelia White","readyTime":710,"dueTime":1080,"actualStartTime":-1,"length":60,"acuity":1,"assignedChair":-1,"assignedNurse":-1},{"patientId":14,"patientMRN":5354061492,"patientName":"Logan Harris","readyTime":820,"dueTime":1080,"actualStartTime":-1,"length":60,"acuity":1,"assignedChair":-1,"assignedNurse":-1},{"patientId":15,"patientMRN":9769905005,"patientName":"Harper Martin","readyTime":960,"dueTime":1080,"actualStartTime":-1,"length":60,"acuity":3,"assignedChair":-1,"assignedNurse":-1},{"patientId":16,"patientMRN":4766374036,"patientName":"Lucas Thompson","readyTime":580,"dueTime":1080,"actualStartTime":-1,"length":60,"acuity":2,"assignedChair":-1,"assignedNurse":-1},{"patientId":17,"patientMRN":2443149469,"patientName":"Evelyn Garcia","readyTime":950,"dueTime":1080,"actualStartTime":-1,"length":60,"acuity":3,"assignedChair":-1,"assignedNurse":-1},{"patientId":18,"patientMRN":8903501835,"patientName":"Jackson Martinez","readyTime":630,"dueTime":1080,"actualStartTime":-1,"length":60,"acuity":2,"assignedChair":-1,"assignedNurse":-1},{"patientId":19,"patientMRN":1303166285,"patientName":"Abigail Robinson","readyTime":570,"dueTime":1080,"actualStartTime":-1,"length":60,"acuity":1,"assignedChair":-1,"assignedNurse":-1},{"patientId":20,"patientMRN":6004182118,"patientName":"Aiden Clark","readyTime":540,"dueTime":1080,"actualStartTime":-1,"length":60,"acuity":3,"assignedChair":-1,"assignedNurse":-1},{"patientId":21,"patientMRN":7388947881,"patientName":"Ella Rodriguez","readyTime":690,"dueTime":1080,"actualStartTime":-1,"length":60,"acuity":3,"assignedChair":-1,"assignedNurse":-1},{"patientId":22,"patientMRN":8166308744,"patientName":"Oliver Lewis","readyTime":670,"dueTime":1080,"actualStartTime":-1,"length":60,"acuity":1,"assignedChair":-1,"assignedNurse":-1},{"patientId":23,"patientMRN":5347248470,"patientName":"Grace Lee","readyTime":770,"dueTime":1080,"actualStartTime":-1,"length":60,"acuity":2,"assignedChair":-1,"assignedNurse":-1},{"patientId":24,"patientMRN":7976483495,"patientName":"Alexander Walker","readyTime":510,"dueTime":1080,"actualStartTime":-1,"length":60,"acuity":2,"assignedChair":-1,"assignedNurse":-1},{"patientId":25,"patientMRN":4293423824,"patientName":"Scarlett Hall","readyTime":910,"dueTime":1080,"actualStartTime":-1,"length":60,"acuity":3,"assignedChair":-1,"assignedNurse":-1},{"patientId":26,"patientMRN":5571069550,"patientName":"Daniel Allen","readyTime":660,"dueTime":1080,"actualStartTime":-1,"length":60,"acuity":3,"assignedChair":-1,"assignedNurse":-1},{"patientId":27,"patientMRN":2379126504,"patientName":"Aria Young","readyTime":800,"dueTime":1080,"actualStartTime":-1,"length":60,"acuity":2,"assignedChair":-1,"assignedNurse":-1},{"patientId":28,"patientMRN":7871285708,"patientName":"Henry King","readyTime":620,"dueTime":1080,"actualStartTime":-1,"length":60,"acuity":1,"assignedChair":-1,"assignedNurse":-1},{"patientId":29,"patientMRN":6325251123,"patientName":"Chloe Hernandez","readyTime":770,"dueTime":1080,"actualStartTime":-1,"length":60,"acuity":3,"assignedChair":-1,"assignedNurse":-1},{"patientId":30,"patientMRN":1149093099,"patientName":"Matthew Scott","readyTime":710,"dueTime":1080,"actualStartTime":-1,"length":60,"acuity":1,"assignedChair":-1,"assignedNurse":-1},{"patientId":31,"patientMRN":1397650564,"patientName":"Zoey Green","readyTime":910,"dueTime":1080,"actualStartTime":-1,"length":60,"acuity":2,"assignedChair":-1,"assignedNurse":-1},{"patientId":32,"patientMRN":4724121385,"patientName":"Sebastian Adams","readyTime":640,"dueTime":1080,"actualStartTime":-1,"length":60,"acuity":3,"assignedChair":-1,"assignedNurse":-1},{"patientId":33,"patientMRN":3687766231,"patientName":"Penelope Baker","readyTime":1000,"dueTime":1080,"actualStartTime":-1,"length":60,"acuity":3,"assignedChair":-1,"assignedNurse":-1},{"patientId":34,"patientMRN":334862935,"patientName":"Samuel Gonzalez","readyTime":900,"dueTime":1080,"actualStartTime":-1,"length":60,"acuity":1,"assignedChair":-1,"assignedNurse":-1},{"patientId":35,"patientMRN":1906228636,"patientName":"Layla Nelson","readyTime":880,"dueTime":1080,"actualStartTime":-1,"length":60,"acuity":2,"assignedChair":-1,"assignedNurse":-1},{"patientId":36,"patientMRN":8089450031,"patientName":"David Carter","readyTime":490,"dueTime":1080,"actualStartTime":-1,"length":60,"acuity":3,"assignedChair":-1,"assignedNurse":-1},{"patientId":37,"patientMRN":2300754798,"patientName":"Riley Mitchell","readyTime":950,"dueTime":1080,"actualStartTime":-1,"length":60,"acuity":3,"assignedChair":-1,"assignedNurse":-1},{"patientId":38,"patientMRN":6788059632,"patientName":"Joseph Perez","readyTime":610,"dueTime":1080,"actualStartTime":-1,"length":60,"acuity":1,"assignedChair":-1,"assignedNurse":-1},{"patientId":39,"patientMRN":5618200965,"patientName":"Victoria Roberts","readyTime":710,"dueTime":1080,"actualStartTime":-1,"length":60,"acuity":2,"assignedChair":-1,"assignedNurse":-1},{"patientId":40,"patientMRN":5401988557,"patientName":"Wyatt Turner","readyTime":950,"dueTime":1080,"actualStartTime":-1,"length":120,"acuity":3,"assignedChair":-1,"assignedNurse":-1},{"patientId":41,"patientMRN":1614249607,"patientName":"Nora Phillips","readyTime":510,"dueTime":1080,"actualStartTime":-1,"length":120,"acuity":3,"assignedChair":-1,"assignedNurse":-1},{"patientId":42,"patientMRN":6340074191,"patientName":"Gabriel Campbell","readyTime":900,"dueTime":1080,"actualStartTime":-1,"length":120,"acuity":2,"assignedChair":-1,"assignedNurse":-1},{"patientId":43,"patientMRN":9355559853,"patientName":"Lily Parker","readyTime":940,"dueTime":1080,"actualStartTime":-1,"length":120,"acuity":2,"assignedChair":-1,"assignedNurse":-1},{"patientId":44,"patientMRN":1163180763,"patientName":"Carter Evans","readyTime":590,"dueTime":1080,"actualStartTime":-1,"length":120,"acuity":1,"assignedChair":-1,"assignedNurse":-1},{"patientId":45,"patientMRN":5024840721,"patientName":"Hannah Edwards","readyTime":570,"dueTime":1080,"actualStartTime":-1,"length":120,"acuity":1,"assignedChair":-1,"assignedNurse":-1},{"patientId":46,"patientMRN":7247516122,"patientName":"Jayden Collins","readyTime":570,"dueTime":1080,"actualStartTime":-1,"length":120,"acuity":1,"assignedChair":-1,"assignedNurse":-1},{"patientId":47,"patientMRN":2709346475,"patientName":"Lillian Stewart","readyTime":800,"dueTime":1080,"actualStartTime":-1,"length":120,"acuity":3,"assignedChair":-1,"assignedNurse":-1},{"patientId":48,"patientMRN":3948669134,"patientName":"John Sanchez","readyTime":910,"dueTime":1080,"actualStartTime":-1,"length":120,"acuity":3,"assignedChair":-1,"assignedNurse":-1},{"patientId":49,"patientMRN":6635061364,"patientName":"Natalie Morris","readyTime":940,"dueTime":1080,"actualStartTime":-1,"length":120,"acuity":3,"assignedChair":-1,"assignedNurse":-1},{"patientId":50,"patientMRN":304774227,"patientName":"Owen Rogers","readyTime":760,"dueTime":1080,"actualStartTime":-1,"length":120,"acuity":1,"assignedChair":-1,"assignedNurse":-1},{"patientId":51,"patientMRN":712879048,"patientName":"Lucy Reed","readyTime":700,"dueTime":1080,"actualStartTime":-1,"length":120,"acuity":1,"assignedChair":-1,"assignedNurse":-1},{"patientId":52,"patientMRN":7078569766,"patientName":"Dylan Cook","readyTime":940,"dueTime":1080,"actualStartTime":-1,"length":120,"acuity":2,"assignedChair":-1,"assignedNurse":-1},{"patientId":53,"patientMRN":4698625995,"patientName":"Brooklyn Morgan","readyTime":520,"dueTime":1080,"actualStartTime":-1,"length":120,"acuity":3,"assignedChair":-1,"assignedNurse":-1},{"patientId":54,"patientMRN":903661064,"patientName":"Luke Bell","readyTime":930,"dueTime":1080,"actualStartTime":-1,"length":120,"acuity":2,"assignedChair":-1,"assignedNurse":-1},{"patientId":55,"patientMRN":8498315302,"patientName":"Violet Murphy","readyTime":950,"dueTime":1080,"actualStartTime":-1,"length":120,"acuity":2,"assignedChair":-1,"assignedNurse":-1},{"patientId":56,"patientMRN":1807860877,"patientName":"Levi Bailey","readyTime":730,"dueTime":1080,"actualStartTime":-1,"length":120,"acuity":1,"assignedChair":-1,"assignedNurse":-1},{"patientId":57,"patientMRN":8116609021,"patientName":"Stella Rivera","readyTime":780,"dueTime":1080,"actualStartTime":-1,"length":120,"acuity":3,"assignedChair":-1,"assignedNurse":-1},{"patientId":58,"patientMRN":6155403822,"patientName":"Isaac Cooper","readyTime":600,"dueTime":1080,"actualStartTime":-1,"length":120,"acuity":3,"assignedChair":-1,"assignedNurse":-1},{"patientId":59,"patientMRN":7175816984,"patientName":"Zoe Richardson","readyTime":730,"dueTime":1080,"actualStartTime":-1,"length":120,"acuity":2,"assignedChair":-1,"assignedNurse":-1},{"patientId":60,"patientMRN":4075230844,"patientName":"Hunter Cox","readyTime":620,"dueTime":1080,"actualStartTime":-1,"length":120,"acuity":2,"assignedChair":-1,"assignedNurse":-1},{"patientId":61,"patientMRN":6745396749,"patientName":"Aurora Howard","readyTime":760,"dueTime":1080,"actualStartTime":-1,"length":120,"acuity":3,"assignedChair":-1,"assignedNurse":-1},{"patientId":62,"patientMRN":9074051968,"patientName":"Eli Ward","readyTime":810,"dueTime":1080,"actualStartTime":-1,"length":120,"acuity":3,"assignedChair":-1,"assignedNurse":-1},{"patientId":63,"patientMRN":6476015386,"patientName":"Savannah Cox","readyTime":920,"dueTime":1080,"actualStartTime":-1,"length":120,"acuity":3,"assignedChair":-1,"assignedNurse":-1},{"patientId":64,"patientMRN":228361650,"patientName":"Jack Torres","readyTime":620,"dueTime":1080,"actualStartTime":-1,"length":120,"acuity":3,"assignedChair":-1,"assignedNurse":-1},{"patientId":65,"patientMRN":8654244587,"patientName":"Addison Peterson","readyTime":490,"dueTime":1080,"actualStartTime":-1,"length":120,"acuity":3,"assignedChair":-1,"assignedNurse":-1},{"patientId":66,"patientMRN":3045260814,"patientName":"Julian Gray","readyTime":610,"dueTime":1080,"actualStartTime":-1,"length":120,"acuity":3,"assignedChair":-1,"assignedNurse":-1},{"patientId":67,"patientMRN":3612592482,"patientName":"Ellie Ramirez","readyTime":760,"dueTime":1080,"actualStartTime":-1,"length":120,"acuity":2,"assignedChair":-1,"assignedNurse":-1},{"patientId":68,"patientMRN":3291872974,"patientName":"Ryan James","readyTime":760,"dueTime":1080,"actualStartTime":-1,"length":120,"acuity":1,"assignedChair":-1,"assignedNurse":-1},{"patientId":69,"patientMRN":7738744966,"patientName":"Audrey Hughes","readyTime":880,"dueTime":1080,"actualStartTime":-1,"length":120,"acuity":3,"assignedChair":-1,"assignedNurse":-1},{"patientId":70,"patientMRN":2521695090,"patientName":"Michael Price","readyTime":760,"dueTime":1080,"actualStartTime":-1,"length":240,"acuity":2,"assignedChair":-1,"assignedNurse":-1},{"patientId":71,"patientMRN":252802642,"patientName":"Leah Reed","readyTime":590,"dueTime":1080,"actualStartTime":-1,"length":240,"acuity":2,"assignedChair":-1,"assignedNurse":-1},{"patientId":72,"patientMRN":8781672945,"patientName":"Asher Butler","readyTime":730,"dueTime":1080,"actualStartTime":-1,"length":240,"acuity":3,"assignedChair":-1,"assignedNurse":-1},{"patientId":73,"patientMRN":3079748967,"patientName":"Paisley Barnes","readyTime":840,"dueTime":1080,"actualStartTime":-1,"length":240,"acuity":3,"assignedChair":-1,"assignedNurse":-1},{"patientId":74,"patientMRN":1561377268,"patientName":"Christopher Jenkins","readyTime":760,"dueTime":1080,"actualStartTime":-1,"length":240,"acuity":1,"assignedChair":-1,"assignedNurse":-1},{"patientId":75,"patientMRN":7620504314,"patientName":"Camila Perry","readyTime":790,"dueTime":1080,"actualStartTime":-1,"length":240,"acuity":1,"assignedChair":-1,"assignedNurse":-1},{"patientId":76,"patientMRN":2393452139,"patientName":"Josiah Russell","readyTime":500,"dueTime":1080,"actualStartTime":-1,"length":240,"acuity":3,"assignedChair":-1,"assignedNurse":-1},{"patientId":77,"patientMRN":7227259194,"patientName":"Scarlett Cook","readyTime":740,"dueTime":1080,"actualStartTime":-1,"length":240,"acuity":1,"assignedChair":-1,"assignedNurse":-1},{"patientId":78,"patientMRN":3239942845,"patientName":"Andrew Sanders","readyTime":720,"dueTime":1080,"actualStartTime":-1,"length":240,"acuity":2,"assignedChair":-1,"assignedNurse":-1},{"patientId":79,"patientMRN":4745834849,"patientName":"Isla Simmons","readyTime":780,"dueTime":1080,"actualStartTime":-1,"length":240,"acuity":1,"assignedChair":-1,"assignedNurse":-1},{"patientId":80,"patientMRN":9755413317,"patientName":"Thomas Foster","readyTime":840,"dueTime":1080,"actualStartTime":-1,"length":240,"acuity":3,"assignedChair":-1,"assignedNurse":-1},{"patientId":81,"patientMRN":962916776,"patientName":"Clara Gonzales","readyTime":670,"dueTime":1080,"actualStartTime":-1,"length":240,"acuity":2,"assignedChair":-1,"assignedNurse":-1},{"patientId":82,"patientMRN":1945990340,"patientName":"Nathan Bryant","readyTime":620,"dueTime":1080,"actualStartTime":-1,"length":240,"acuity":3,"assignedChair":-1,"assignedNurse":-1},{"patientId":83,"patientMRN":8269564546,"patientName":"Elena Butler","readyTime":760,"dueTime":1080,"actualStartTime":-1,"length":240,"acuity":2,"assignedChair":-1,"assignedNurse":-1},{"patientId":84,"patientMRN":3945875207,"patientName":"Caleb Alexander","readyTime":630,"dueTime":1080,"actualStartTime":-1,"length":240,"acuity":2,"assignedChair":-1,"assignedNurse":-1},{"patientId":85,"patientMRN":4349093951,"patientName":"Ruby Reynolds","readyTime":550,"dueTime":1080,"actualStartTime":-1,"length":240,"acuity":2,"assignedChair":-1,"assignedNurse":-1},{"patientId":86,"patientMRN":6945921226,"patientName":"Henry Wallace","readyTime":730,"dueTime":1080,"actualStartTime":-1,"length":240,"acuity":3,"assignedChair":-1,"assignedNurse":-1},{"patientId":87,"patientMRN":3853619442,"patientName":"Samantha Webb","readyTime":640,"dueTime":1080,"actualStartTime":-1,"length":240,"acuity":1,"assignedChair":-1,"assignedNurse":-1},{"patientId":88,"patientMRN":1917402191,"patientName":"Christian Hayes","readyTime":560,"dueTime":1080,"actualStartTime":-1,"length":240,"acuity":1,"assignedChair":-1,"assignedNurse":-1},{"patientId":89,"patientMRN":5011366355,"patientName":"Stella Alexander","readyTime":800,"dueTime":1080,"actualStartTime":-1,"length":240,"acuity":3,"assignedChair":-1,"assignedNurse":-1},{"patientId":90,"patientMRN":3568300360,"patientName":"Jonathan Curtis","readyTime":520,"dueTime":1080,"actualStartTime":-1,"length":480,"acuity":1,"assignedChair":-1,"assignedNurse":-1},{"patientId":91,"patientMRN":1066957847,"patientName":"Mila Bowman","readyTime":530,"dueTime":1080,"actualStartTime":-1,"length":480,"acuity":3,"assignedChair":-1,"assignedNurse":-1},{"patientId":92,"patientMRN":2962534082,"patientName":"Aaron Matthews","readyTime":490,"dueTime":1080,"actualStartTime":-1,"length":480,"acuity":2,"assignedChair":-1,"assignedNurse":-1},{"patientId":93,"patientMRN":8761732956,"patientName":"Hazel Russell","readyTime":500,"dueTime":1080,"actualStartTime":-1,"length":480,"acuity":1,"assignedChair":-1,"assignedNurse":-1},{"patientId":94,"patientMRN":4958778728,"patientName":"Jeremiah Hamilton","readyTime":500,"dueTime":1080,"actualStartTime":-1,"length":480,"acuity":3,"assignedChair":-1,"assignedNurse":-1},{"patientId":95,"patientMRN":4543219847,"patientName":"Victoria Hayes","readyTime":570,"dueTime":1080,"actualStartTime":-1,"length":480,"acuity":2,"assignedChair":-1,"assignedNurse":-1},{"patientId":96,"patientMRN":8183452587,"patientName":"Adrian Griffin","readyTime":500,"dueTime":1080,"actualStartTime":-1,"length":480,"acuity":1,"assignedChair":-1,"assignedNurse":-1},{"patientId":97,"patientMRN":703432126,"patientName":"Lucy Hamilton","readyTime":510,"dueTime":1080,"actualStartTime":-1,"length":480,"acuity":1,"assignedChair":-1,"assignedNurse":-1},{"patientId":98,"patientMRN":1689636567,"patientName":"Cameron Hayes","readyTime":480,"dueTime":1080,"actualStartTime":-1,"length":600,"acuity":2,"assignedChair":-1,"assignedNurse":-1},{"patientId":99,"patientMRN":3211035187,"patientName":"Nora Sims","readyTime":480,"dueTime":1080,"actualStartTime":-1,"length":600,"acuity":2,"assignedChair":-1,"assignedNurse":-1}],"nurses":[{"nurseId":0,"nurseName":"Jessica Thompson","nurseEmail":"jessica.thompson@upenn.edu","assignedPatients":[],"startTime":480,"endTime":1080},{"nurseId":1,"nurseName":"Michael Johnson","nurseEmail":"michael.johnson@upenn.edu","assignedPatients":[],"startTime":480,"endTime":1080},{"nurseId":2,"nurseName":"Sarah Williams","nurseEmail":"sarah.williams@upenn.edu","assignedPatients":[],"startTime":480,"endTime":1080},{"nurseId":3,"nurseName":"David Brown","nurseEmail":"david.brown@upenn.edu","assignedPatients":[],"startTime":480,"endTime":1080},{"nurseId":4,"nurseName":"Emily Jones","nurseEmail":"emily.jones@upenn.edu","assignedPatients":[],"startTime":480,"endTime":1080},{"nurseId":5,"nurseName":"Matthew Garcia","nurseEmail":"matthew.garcia@upenn.edu","assignedPatients":[],"startTime":480,"endTime":1080},{"nurseId":6,"nurseName":"Olivia Miller","nurseEmail":"olivia.miller@upenn.edu","assignedPatients":[],"startTime":480,"endTime":1080},{"nurseId":7,"nurseName":"Christopher Martinez","nurseEmail":"christopher.martinez@upenn.edu","assignedPatients":[],"startTime":480,"endTime":1080},{"nurseId":8,"nurseName":"Sophia Davis","nurseEmail":"sophia.davis@upenn.edu","assignedPatients":[],"startTime":480,"endTime":1080},{"nurseId":9,"nurseName":"Daniel Rodriguez","nurseEmail":"daniel.rodriguez@upenn.edu","assignedPatients":[],"startTime":480,"endTime":1080},{"nurseId":10,"nurseName":"Isabella Hernandez","nurseEmail":"isabella.hernandez@upenn.edu","assignedPatients":[],"startTime":480,"endTime":1080},{"nurseId":11,"nurseName":"Isabella Hernandez","nurseEmail":"isabella.hernandez@upenn.edu","assignedPatients":[],"startTime":480,"endTime":1080}],"chairs":[],"settings":{"goals":null,"numberOfChairs":36,"break_duration":30,"break_end_time":750,"break_start_time":690,"openTime":480,"patientNurseRatio":4,"closeTime":1080}}'
    # Example usage
    uri, id, date, num_nurses, num_chairs, M, open_time, close_time, patients, nurses, chairs, break_start_time, break_end_time, break_duration = parse_json(
        input_json)

    naive_allocation = generate_naive_allocation(patients, nurses, num_chairs, open_time, close_time)
    allocation = schedule_patients_no_set_lunch(patients, num_chairs, num_nurses, open_time, close_time, M,
                                                break_start_time, break_end_time, break_duration)

    if allocation is None:
        allocation = schedule_patients_no_constraint(patients, num_chairs, num_nurses, open_time, close_time, M,
                                                     break_start_time, break_end_time, break_duration)

    optimized_roi = calculate_roi_metrics(allocation, patients, nurses, open_time, close_time, break_start_time,
                                          break_end_time,
                                          break_duration)

    unoptimized_roi = calculate_roi_metrics(naive_allocation, patients, nurses, open_time, close_time,
                                            break_start_time,
                                            break_end_time,
                                            break_duration)

    if not prod:
        for alloc in allocation:
            print(
                f"Patient {alloc[0]} starts at {alloc[1]} and ends at {alloc[2]} in chair {alloc[3]} with nurse {alloc[4]}")

        print("ROI FROM OPTIMIZED SCHEDULE")

        print(optimized_roi)

        print("ROI FROM NAIVE SCHEDULE")

        print(unoptimized_roi)

    schedule_json = create_schedule_json(date, patients, nurses, allocation, naive_allocation, num_chairs, open_time, close_time)
    roi_json = create_roi_json(date, optimized_roi, unoptimized_roi)

    # MongoDB's connection details
    db_name = 'Paoli'

    # Connect to MongoDB and update the schedule
    client = connect_to_mongo(uri)
    db = client[db_name]
    upload_schedule(db, 'schedules', schedule_json)
    upload_roi(db, 'roi_metrics', roi_json)

    # Close the connection
    client.close()

    print("Python Script Completed!")


if __name__ == "__main__":
    main()
