import os
import glob
import random
import shutil
import string
import zipfile

import magic

from ConfigParser import SafeConfigParser

TEMPLATE_UPLOAD_DIR = os.path.join(os.getcwd(), "templates", "spoofed_website_templates")
REQUIRED_TEMPLATE_CONF = { "name": str,
                           "injection_enabled": bool,
                           "credential_hijack_enabled": bool
                         }

########[ Helper Scripts for new template ]########
def generate_random_string(min_l=6, max_l=15):
    return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + \
        string.digits) for _ in range(random.randint(min_l, max_l)))

def generate_path(path):
    while True:
        file_path = os.path.join(path, generate_random_string())
        if not os.path.exists(file_path):
           return file_path

def allowed_file(f):
    allowed_types = ["application/zip"]
    file_type = magic.from_file(f, mime=True) 
    if file_type in allowed_types:
        return file_type
    else:
        return False

def template_unzip(path):
    try:
        zip_f = zipfile.ZipFile(path, 'r')
        output_dir = generate_path(TEMPLATE_UPLOAD_DIR)
        zip_f.extractall(output_dir)
        zip_f.close()
    except:
        try:
            shutil.rmtree(output_dir)
        except OSError:
            pass
        return False
    else:
        return output_dir
    finally:
        os.remove(path)

def validate_template(directory_path):
    if not directory_path or not os.path.isfile(os.path.join(directory_path, "config.ini")):
        return False

    parser = SafeConfigParser()
    with open(os.path.join(directory_path, "config.ini")) as f:
        parser.readfp(f)

    try:
        for k, v in REQUIRED_TEMPLATE_CONF.items():
           value = parser.get('template', k)
           try:
              if v is bool:
                  bool(value)
              if v is int:
                  int(value)
           except ValueError:
              return False
    except ConfigParser.NoSectionError:
        shutil.rmtree(directory_path)
        return False
    else:
        return True

###########[ Main functions ]##############################
def upload_new_template(request):
    n_file = request.files['files[]']
    
    while True:
        file_path = generate_path(TEMPLATE_UPLOAD_DIR)
        if not os.path.exists(file_path):
            break

    if not n_file:
        return False
    else:
        n_file.save(file_path)
    
    file_type = allowed_file(file_path)

    if file_type == "application/zip":
        status = validate_template(template_unzip(file_path))
    else:
        os.remove(file_path)
        status = False
    
    return status
    
def get_templates():
    templates_directory = os.path.join(os.getcwd(), "templates", "spoofed_website_templates")
    inis = glob.glob(os.path.join(templates_directory, "*", "config.ini"))

    template_data = []
    for ini in inis:
        parser = SafeConfigParser()
        with open(ini) as f:
            parser.readfp(f)

        template_name = parser.get('template', 'name')
        injection = parser.get('template', 'injection_enabled')
        credential_hijack = parser.get('template', 'credential_hijack_enabled')
        directory = os.path.dirname(ini)

        template_data.append([template_name, injection, credential_hijack, directory])

    return template_data
