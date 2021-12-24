import json_to_color_patch
import patch_vmts
from flask import Flask, request, send_file, after_this_request
from flask_cors import CORS
import shutil
import time
import vpk
import os
import io
from multiprocessing import Process

app = Flask(__name__)
CORS(app, expose_headers=["Content-Disposition"])

@app.route('/generate', methods=['POST'])
def generate():
    if request.method == 'POST':
        requestTime = str(int(time.time()))
        data = request.get_json()
        # shutil.rmtree("work/", ignore_errors=True)
        shutil.copytree("materials/", "work/" + requestTime + "/materials/")
        shutil.copytree("template/particles", "work/" + requestTime + "/particles/")

        # print('Data Received: "{data}"'.format(data=data))
        print("New request: " + requestTime);
        red_crit = data['material']['red_crit']['color']
        red_minicrit = data['material']['red_minicrit']['color']
        blue_crit = data['material']['blue_crit']['color']
        blue_minicrit = data['material']['blue_minicrit']['color']
        patch_vmts.patchVMTs(blue_crit, red_crit, red_minicrit, blue_minicrit, "work/" + requestTime + "/materials/")
        print("Patched vmts!");
        
        del data['material'] #clean up the stuff thats only for vmfs
        json_to_color_patch.patchPCFWithJson(data, "work/" + requestTime + "/particles/")
        print("Patched particles!");
        
        newpak = vpk.new("work/" + requestTime)
        newpak.save("colors.tf_" + requestTime + ".vpk")
        print("Packed files!");

        filename = "colors.tf_" + requestTime + ".vpk"
        
        return_data = io.BytesIO()
        with open(filename, 'rb') as fo:
            return_data.write(fo.read())
            return_data.seek(0)    

        background_remove(filename)
    
        return send_file(return_data, as_attachment=True, attachment_filename=filename)

def background_remove(path):
    task = Process(target=rm(path))
    task.start()

    
def rm(path):
    os.remove(path)

if __name__ == "__main__":
#   app.run(port=3000)
  # if you need to make it live debuging add 'debug=True'
  app.run(port=3000, debug=True)
