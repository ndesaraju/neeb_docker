import flywheel
from datetime import datetime
import subprocess as sp
import kangaroos
import numpy as np
import pdb

group_id = "processing"
project_id = "neeb"

def flywheel_login(login_key):
    start = datetime.now()
    fw = flywheel.Client(login_key)
    end = datetime.now()

    user = fw.get_current_user()
    print("Logged in with user: %s %s!" % (user.firstname, user.lastname))
    print("User login took {} (hh:mm:ss.ms)\n".format(end - start))
    return fw

def find_project(fw, group_id, project_id):
    # Get the project, e.g. siena_testing
    start = datetime.now()
    location = group_id + "/" + project_id
    print("Looking for project at", location)
    project = fw.lookup(location)
    end = datetime.now()
    print("Found project!")

    num_subjects = len(project.subjects())
    num_exams = len(project.sessions())
    num_analyses = len(project.analyses)
    print("Project lookup took {0} (hh:mm:ss.ms) with {1} subjects, {2} exams, and {3} analyses\n".format(end - start, num_subjects,
                                                                                         num_exams, num_analyses))
    return project

def get_file(acquisition):
	for file in acquisition.files:
		if "dicom" in file.name:
			return file

def find_dicoms(acquisitions):
	dicoms = {}
	meget1_nums = []
	meget1_acq = []
	meget2_nums = []
	meget2_acq = []

	for acq in acquisitions:
		label = acq.label
		if "epi_bh30" in label:
			dicoms["epi_bh30"] = get_file(acq)
		if "epi_bh90" in label:
			dicoms["epi_bh90"] = get_file(acq)
		if "MEGET1" in label:
			meget1_nums.append(int(label.split("-")[0]))
			meget1_acq.append(acq)
		if "epi_bb90" in label:
			dicoms["epi_bb90"] = get_file(acq)
		if "MEGET2star" in label:
			meget2_nums.append(int(label.split("-")[0]))
			meget2_acq.append(acq)

	max_ind1 = np.argmax(np.asarray(meget1_nums))
	min_ind1 = np.argmin(np.asarray(meget1_nums))
	dicoms["MEGET1"] = get_file(meget1_acq[min_ind1])
	dicoms["MEGET1_intensities"] = get_file(meget1_acq[max_ind1])
	max_ind2 = np.argmax(np.asarray(meget2_nums))
	min_ind2 = np.argmin(np.asarray(meget2_nums))
	dicoms["MEGET2star"] = get_file(meget2_acq[min_ind2])
	dicoms["MEGET2star_intensities"] = get_file(meget2_acq[max_ind2])
	to_copy = {}
	#pdb.set_trace()
	if "epi_bh30" in dicoms.keys() and "epi_bh90" in dicoms.keys() and "MEGET1" in dicoms.keys()  and "epi_bb90" in dicoms.keys()  and "MEGET1_intensities" in dicoms.keys()  and "MEGET2star" in dicoms.keys()  and "MEGET2star_intensities" in dicoms.keys():
		print("All dicoms found needed for Neeb.")
		return dicoms
	else:
		missing = []
		if "epi_bh30" not in dicoms.keys():
			missing += ["epi_bh30"]
		if "epi_bh90" not in dicoms.keys():
			missing += ["epi_bh90"]
		if "MEGET1" not in dicoms.keys():
			missing += ["MEGET1"]
		if "MEGET1_intensities" not in dicoms.keys():
			missing += ["MEGET1_intensities"]
		if "MEGET2star" not in dicoms.keys():
			missing += ["MEGET2star"]
		if "MEGET2star_intensities" not in dicoms.keys():
			missing += ["MEGET2star_intensities"]
		if "epi_bb90" not in dicoms.keys():
			missing += ["epi_bb90"]
		raise RuntimeError("Missing the following dicoms: {0}".format(missing))

def run_neeb(login_key, mseID):
	fw = flywheel_login(login_key)
	#(1) go to the Neeb project in the processing group and query for a specific session ID
	#* you may need to look up the subject ID to do this or query through the entire list not sure I would start by looking at the Flywheel API
	try:
		project = find_project(fw, group_id, project_id)
	except:
		raise RuntimeError("Could not find project...")

	dicoms = None
	print("looking for session in project...")
	for session in project.sessions.iter():
		if session.label == mseID:
			print("found session {0}".format(session.label))
			if session.acquisitions():
				dicoms = find_dicoms(session.acquisitions())
				break
	#2) after you find the session ID, list all the acquisitions
	#-> identify if the appropriate data is there to run Neeb. You should have already written a script similar to this


	#(3) If all the data is there, lookup the Neeb gear and run it
	#-> the run_siena function has an example of doing this for the SIENA gear
	gear = fw.lookup("gears/neeb")
	analysis_label = "Neeb "
	config = {}
	#pdb.set_trace()
	analysis_id = gear.run(analysis_label=analysis_label, config=config, inputs=dicoms,
                                               destination=session, tags=['ran from neeb_gear script'])
	# info = {'mseID': mseID, 'date': date, 'file': file.name}
	# print("Updating analysis %s with custom info to include exam and date..." % analysis_id)
 #                    update = flywheel.models.InfoUpdateInput(set=info)
 #    fw.modify_analysis_info(analysis_id, update)
	print("Gear ran for mseID %s, your analysis ID is %s\n" % (mseID, analysis_id))

run_neeb("ucsfbeta.flywheel.io:FWWI9f6ZNlcyxZAqz6", "mse14092")

