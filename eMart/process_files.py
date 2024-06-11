import datetime
import os
import csv
import smtplib
import ssl


today = str(datetime.date.today())
folder_name = today[:4] + today[5:7] + today[8:]
product_master_list = []
incoming_file_count=0
error_file_count = 0
###read_master_file() is reafing master file and holding data in dictionary


def read_master_file():
    with open("product_master.csv", "r") as data:
        for line in csv.DictReader(data):
            product_master_list.append(line)
    return product_master_list

###read_incoming_files() is reading incoming file from today's date folder and holding it in dictionary
def read_incoming_files():
    incoming_files_list = []
    try:
        incoming_files = os.listdir("incoming_files/"+ folder_name+"/")
    except FileNotFoundError:
        print(f"file not found for {today}")
        send_email()
    for file in incoming_files:
        read_file_and_create_list(file)
    global incoming_file_count
    incoming_file_count = len(incoming_files)
    return incoming_files_list

def read_file_and_create_list(file):
    incoming_files_list = []
    with open("incoming_files/" + folder_name + "/" + file, 'r') as data:
        for line in csv.DictReader(data):
            incoming_files_list.append(line)
    validation_erorr_file_creation(incoming_files_list,file)
def validation_erorr_file_creation(incoming_files_list,file):
    reason_list = []
    header_list=['order_id','order_date','product_id','quantity','sales','city','reason']
    error_flag=0
    header_flag = 1
    for order in incoming_files_list:
        incorrect_record_reason=[]
        if order['city'] != 'Bangalore' and order['city'] != 'Mumbai':
            incorrect_record_reason.append('Location is not correct')
        order_date_str = order['order_date']
        order_date = datetime.datetime.strptime(order_date_str, "%d-%m-%Y").date()
        if order_date > datetime.date.today():
            incorrect_record_reason.append('Order Date is from future')
        for key,val in order.items():
            if val==None or val=='':
                incorrect_record_reason.append(f"{key} is empty")
        if check_product_presence(order):
            print('from check product_presence-test')
            incorrect_record_reason.append("product not exists")
        if check_ordered_product_price(order):
            print('check_ordered_product_price')
            incorrect_record_reason.append("price not accurate")
        print(incorrect_record_reason)

        if incorrect_record_reason:
            order['reason'] = incorrect_record_reason
            if not os.path.exists("rejected_files/" + folder_name):
                os.makedirs("rejected_files/" + folder_name)
            error_file = open("rejected_files/" + folder_name + "/" + "error_" + file, "a", newline='')
            writer = csv.DictWriter(error_file, fieldnames=header_list)
            if header_flag:
                writer.writeheader()
                header_flag = 0
            writer.writerow(order)
            error_file.close()
            reason_list = incorrect_record_reason

    if not reason_list:
       move_file_success_reject(error_flag, file)
    else:
        error_flag=1
        global error_file_count
        error_file_count+=1
        move_file_success_reject(error_flag, file)

def move_file_success_reject(error_flag,file):

    if not os.path.exists("success_files/" + folder_name):
        os.makedirs("success_files/" + folder_name)
    if not os.path.exists("rejected_files/" + folder_name):
        os.makedirs("rejected_files/" + folder_name)
    if error_flag:
        os.rename("incoming_files/" + folder_name + "/" + file, "rejected_files/" + folder_name + "/" + file)
    else:
        os.rename("incoming_files/" + folder_name + "/" + file, "success_files/" + folder_name + "/" + file)

def check_product_presence(order):
    print(order)
    for key,val in order.items():
        if key == 'product_id':
            if check_product_id(val)==0:
                return 1
            else:
                return 0


def check_product_id(ordered_product_id):
    flag=0
    print(ordered_product_id)
    for order in product_master_list:
        for key,val in order.items():
            if key == 'product_id':
                if val==ordered_product_id:
                    print(val)
                    print(ordered_product_id)
                    flag=1
                    break
    return flag

def check_ordered_product_price(order):
    flag=1
    ordered_product_price = int(order['sales'])
    ordered_product_quantity = int(order['quantity'])
    order_product_id = order['product_id']
    for product in product_master_list:
        for key, val in product.items():
            if key == 'product_id' and val == order_product_id:
                if ordered_product_price == ordered_product_quantity * int(product['price']):
                    flag = 0
                    break
    return flag


def send_email():
    import smtplib
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login("sender_email@gmail.com", "password")
    # message to be sent
    subject = f"validation email {today}"
    message = f"total {incoming_file_count} incoming files , {error_file_count} successsful files and {incoming_file_count-error_file_count} rejected files for that day."
    s.sendmail("sender_email@gmail.com", "receiver_email@gmail.com", subject,message)
    # terminating the session
    s.quit()


read_master_file()
read_incoming_files()
print(incoming_file_count)
print(error_file_count)
send_email()




