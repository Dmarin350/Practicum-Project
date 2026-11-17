"""Creating a case with a new patient also gives that patient a portal login
whose username and password are both their name, and the portal shows the
information entered for them."""

from tests.conftest import sign_in


def new_patient(first, last, **extra):
    return {
        "first_name": first,
        "last_name": last,
        "preferred_name": None,
        "date_of_birth": "1990-04-12",
        "gender_at_birth": "Female",
        "gender_identity": "Woman",
        "pronouns": "she/her",
        "create_portal_account": True,
        **extra,
    }


def test_new_case_patient_can_sign_in_and_see_their_chart(api, instructor, unique):
    last = f"Case{unique}"
    created = instructor.post("/patients", json=new_patient("Rosa", last, preferred_name="Rosie"))
    assert created.status_code == 201, created.text
    patient = created.json()
    username = f"rosa{last.lower()}"
    assert patient["portal_username"] == username

    # Chart data is saved with the case, as the Create Case page does
    case = instructor.post("/cases", json={
        "patient_id": patient["patient_id"],
        "chief_complaint": "Shortness of breath",
        "created_by_staff_id": instructor.me["staffid"],
        "medications": [{"drug_name": "Albuterol", "dose": "90mcg", "route": None, "frequency": None}],
        "allergies": [{"substance": "Penicillin", "reaction": "Hives"}],
        "labs": [{"test_name": "WBC", "result": "11.2", "unit": "K/uL", "flag": "High",
                  "collected_at": "2026-11-01T08:00"}],
    })
    assert case.status_code == 201, case.text

    # Username and password are both the patient's name
    portal = sign_in(api, username, username)
    assert portal.me["role"] == "PATIENT"
    assert portal.me["patientid"] == patient["patient_id"]

    me = portal.get("/portal/me").json()
    assert (me["first_name"], me["last_name"], me["preferred_name"]) == ("Rosa", last, "Rosie")
    assert me["date_of_birth"] == "1990-04-12"
    assert me["pronouns"] == "she/her"
    assert [a["substance"] for a in portal.get("/portal/allergies").json()] == ["Penicillin"]
    assert [m["name"] for m in portal.get("/portal/medications").json()] == ["Albuterol"]
    assert [l["test_name"] for l in portal.get("/portal/lab-results").json()] == ["WBC"]


def test_same_name_gets_a_numbered_username(instructor, unique):
    last = f"Twin{unique}"
    first = instructor.post("/patients", json=new_patient("Ana", last)).json()
    second = instructor.post("/patients", json=new_patient("Ana", last)).json()
    assert first["portal_username"] == f"ana{last.lower()}"
    assert second["portal_username"] == f"ana{last.lower()}2"


def test_accents_and_punctuation_are_dropped(instructor, unique):
    created = instructor.post("/patients", json=new_patient("José", f"O'Núñez-{unique}")).json()
    assert created["portal_username"] == f"joseonunez{unique}"


def test_no_login_unless_asked(instructor, unique):
    body = new_patient("Plain", f"Patient{unique}")
    del body["create_portal_account"]
    created = instructor.post("/patients", json=body).json()
    assert created["portal_username"] is None


def test_patient_list_still_works(instructor):
    patients = instructor.get("/patients")
    assert patients.status_code == 200
    assert all(p["portal_username"] is None for p in patients.json())
