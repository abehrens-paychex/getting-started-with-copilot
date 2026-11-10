from urllib.parse import quote


def signup_url(activity_name):
    return f"/activities/{quote(activity_name, safe='')}/signup"


def test_root_redirects_to_frontend(client):
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_seeded_data(client):
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert expected_activity in response.json()
    assert response.json()[expected_activity]["participants"]


def test_signup_adds_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "new-student@mergington.edu"

    # Act
    response = client.post(signup_url(activity_name), params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in client.get("/activities").json()[activity_name]["participants"]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    original_participants = client.get("/activities").json()[activity_name]["participants"]

    # Act
    response = client.post(signup_url(activity_name), params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up"}
    participants = client.get("/activities").json()[activity_name]["participants"]
    assert participants == original_participants


def test_signup_rejects_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Club"

    # Act
    response = client.post(signup_url(activity_name), params={"email": "student@mergington.edu"})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_removes_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.delete(signup_url(activity_name), params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    assert email not in client.get("/activities").json()[activity_name]["participants"]


def test_unregister_rejects_absent_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "absent@mergington.edu"
    original_participants = client.get("/activities").json()[activity_name]["participants"]

    # Act
    response = client.delete(signup_url(activity_name), params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Student is not signed up"}
    participants = client.get("/activities").json()[activity_name]["participants"]
    assert participants == original_participants


def test_unregister_rejects_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Club"

    # Act
    response = client.delete(signup_url(activity_name), params={"email": "student@mergington.edu"})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
