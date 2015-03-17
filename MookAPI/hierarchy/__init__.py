from flask import Blueprint
from random import randint

bp = Blueprint("hierarchy", __name__)

import documents
import views

def getTrackValidated(trackId):
	rd = randint(0, 99)
	return (rd < 50)

def getSkillValidated(skillId):
	rd = randint(0, 99)
	return (rd < 50)

def progress(trackId):
	track = documents.Track.get_unique_object_or_404(track_id)
	nbValidatedSkill = 0
	skillList = track.skills()
	for skill in skillList:
		skillValidated = getSkillValidated(skill.id)
		if skillValidated: nbValidatedSkill += 1
	return nbValidatedSkill/len(skillList) if len(skillList) > 0 else 100