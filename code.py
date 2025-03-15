import time
from heartrate_monitor import HeartRateMonitor
import RPi.GPIO as GPIO
from twilio.rest import Client
import matplotlib.pyplot as plt
from collections import deque

GPIO.setmode(GPIO.BCM)
led_pin = 14
buzz_pin = 18
GPIO.setup(led_pin, GPIO.OUT)
GPIO.setup(buzz_pin, GPIO.OUT)
GPIO.PWM(buzz_pin, 440)

hrm = HeartRateMonitor(print_raw = False, print_result = False)
hrm.start_sensor()

num_data_points = 100
bpm_data = deque(maxlen=num_data_points)
spo2_data = deque(maxlen=num_data_points)

account_sid='your_sid'
auth_token='your_auth_token'
client=Client(account_sid, auth_token)

def update_plot():
    plt.clf()
    plt.plot(bpm_data, label='Heart Rate (BPM)')
    plt.plot(spo2_data, label='Oxygen Saturation (%)')
    plt.gcf().canvas.set_window_title("Heartbeat and Oxygen Saturation")
    plt.xlabel('Time')
    plt.ylabel('Value')
    plt.legend()
    plt.pause(0.01)
    

try:
    while True:
        current_bpm = hrm.bpm
        current_spo2 = hrm.spo2
         
        print("BPM is ", current_bpm)
        print("spo2 is ", current_spo2)
        
        bpm_data.append(current_bpm)
        spo2_data.append(current_spo2)
        
        if current_bpm > 0:
            GPIO.output(led_pin, True)

        else:
            GPIO.output(led_pin, False) 
            
            
        if current_bpm < 60 or current_bpm > 100:
            GPIO.output(buzz_pin, GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(buzz_pin, GPIO.LOW)
            message = client.messages \
                     .create(body=f"WARNING! The heartbeat is outside the normal range: {current_bpm}", from_ = '+12345678', to='+98765432')
            
            
        if current_spo2 < 95:
            GPIO.output(buzz_pin, GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(buzz_pin, GPIO.LOW)
            message = client.messages \
                       .create(body=f"WARNING! The oxygen saturation is outside the normal range: {current_spo2}", from_ = '+12345678', to='+98765432')
        
        update_plot()
        time.sleep(0.5)
            
except KeyboardInterrupt:
    pass

finally:
    GPIO.output(led_pin, GPIO.LOW)
    GPIO.output(buzz_pin, GPIO.LOW)
    GPIO.cleanup()
    hrm.stop_sensor()
    print("Exiting")



