import serial
import csv
import time
import os

# -------------------- Serial Configuration --------------------
PORT = "COM7"  # Change if needed
BAUD = 115200
TIMEOUT = 1

# -------------------- File Names --------------------
CSV_FILE = "data_ph.csv"
COMMAND_FILE = "command.txt"

# -------------------- Ensure CSV Header --------------------
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "soil", "temperature", "humidity", "pH"])

# -------------------- Open Serial --------------------
def open_serial():
    while True:
        try:
            s = serial.Serial(PORT, BAUD, timeout=TIMEOUT)
            print(f"✅ Connected to {PORT} @ {BAUD} baud")
            return s
        except Exception as e:
            print("⚠ Could not open serial port:", e)
            time.sleep(2)

arduino = open_serial()
print("\n🌿 Logger started. Press CTRL+C to stop.\n")

# -------------------- Main Loop --------------------
while True:
    try:
        line = arduino.readline().decode(errors="ignore").strip()
        if line:
            # Ignore lines that are clearly not CSV
            if line.startswith("🌿") or line.startswith("🪴"):
                continue

            # Split and strip whitespace
            parts = [p.strip() for p in line.split(",")]

            try:
                if len(parts) == 4:
                    soil = float(parts[0])
                    temp = float(parts[1])
                    hum  = float(parts[2])
                    ph   = float(parts[3])

                    # Append to CSV
                    with open(CSV_FILE, "a", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow([time.time(), soil, temp, hum, ph])

                    print(f"🪴 Logged: Soil={soil}% | Temp={temp}°C | Hum={hum}% | pH={ph}")

                elif len(parts) == 3:
                    soil = float(parts[0])
                    temp = float(parts[1])
                    hum  = float(parts[2])

                    with open(CSV_FILE, "a", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow([time.time(), soil, temp, hum, ""])

                    print(f"🪴 Logged (no pH): Soil={soil}% | Temp={temp}°C | Hum={hum}%")
                else:
                    print("❌ Unexpected serial format:", line)

            except ValueError:
                print("❌ Could not parse line:", line)

        # -------------------- Check Streamlit commands --------------------
        # -------------------- Check Streamlit commands --------------------
        if os.path.exists(COMMAND_FILE):
            with open(COMMAND_FILE, "r") as f:
                cmd = f.read().strip()

            if cmd in ["ON", "OFF"]:
                arduino.write((cmd + "\n").encode("utf-8"))
                arduino.flush()          # force send immediately
                print("⚙ Sent command:", cmd)

            # clear file after sending
            open(COMMAND_FILE, "w").close()


        time.sleep(0.5)

    except serial.SerialException:
        print("⚠ Serial connection lost. Reconnecting...")
        arduino.close()
        time.sleep(2)
        arduino = open_serial()

    except KeyboardInterrupt:
        print("\n🛑 Logging stopped by user.")
        arduino.close()
        break

    except Exception as e:
        print("❌ Error:", e)
        time.sleep(1)
