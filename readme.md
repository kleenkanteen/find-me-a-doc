# Project overview:

1.  Problem:
    There is a lack of updated public information when it comes knowing which family doctors are accepting patients. Last December, I got a family doctor at a nearbly clinic and he wasn't on the peel region site that lists free family doctors. This is Ontario. Other provinces may or many not have their own system. Alberta has a more centralized site. Ontario has none.

    The websites that do try to display this info usually have bad UI/UX. They also lack reviews for each doctor. My mom got a UTI turned serious kidney infection due to her family doctor dismissing her concern of frequent urination as just getting older.

    Reddit posts of people complaining of waiting years to find one:

        - https://www.reddit.com/r/ontario/comments/o5vrrx/finding_a_family_doctor_shouldnt_be_this_hard/

        - https://www.reddit.com/r/ontario/comments/11sx2he/how_do_i_find_a_family_doctor/

        - https://www.reddit.com/r/askTO/comments/v4ltuh/family_doctors_accepting_new_patients_in_the/

    ‘Sounding the alarm’: 1 in 4 Ontarians could be without family doctor by 2026, groups say: https://globalnews.ca/news/10257253/ontarians-family-doctors-2026/

2.  Audience: Anyone looking for a family doctor.

3.  MVP Solution:

    1. Create an updated list of family doctors in Toronto as well as their gender. Do this by calling all clinics monthly, asking 2 questions:
       1. Are any family doctors accepting patients?
       2. If yes, number of male and female doctors accepting patients?
    2. A website to show this data in a intuitive manner. Users just input their address and preferred doctor gender and it gives nearest available doctor. They can also see all available doctors in the map.

4.  Nice to have:

    1. Incorporate a way to see reviews for doctors, post reviews for doctors, zand recommend based on reviews

5.  Website tech stack

    1. Frontend: React
    2. Backend: Python flask server to expose endpoints for twilio to send data to.
    3. Database: Supabase, easy to use serverless postgres.

6.  Other tech tools:
    1. Robot caller: flask server mentioned above + Twilio api to make calls
    2. Speech to text: Twilio
    3. Can run these python script(s) locally
    4. Can store prerecorded voices in google drive and played for the script
    5. Google maps api to get clinic info
7.  Project management + diagramming:
    1. Trello for task management
    2. Excalidraw to show conversation flow

Info we collect from about clinic using google maps API:

- location
- name
- phone number
- rating
- called boolean to keep track of which clinics we finished having a convo with

How we make phone calls to those clinics:

- twilio for making phone calls and also transcribing recepetion replies to speech
- use basic if statements and regex to get through menu and conversate

# Current ways to find a doctor:

The College of Physicians and Surgeons of Ontario website has
a directory of all licensed physicians in Ontario. For some reason this does not include information about physicians accepting new patients. Site: [](https://www.cpso.on.ca/)[https://www.cpso.on.ca/](https://www.cpso.on.ca/)

To find a family doctor in Ontario, multiple sites are available: [](<https://www.cpso.on.ca/en/Public/Services/Find-a-Doctor-(1)/Resources-for-Finding-a-New-Doctor>)[https://www.cpso.on.ca/en/Public/Services/Find-a-Doctor-(1)/Resources-for-Finding-a-New-Doctor](<https://www.cpso.on.ca/en/Public/Services/Find-a-Doctor-(1)/Resources-for-Finding-a-New-Doctor>)

## Current sites are outdated research:

## Peel Region Family Doc Site

Peel region accepting doctors: https://www.thp.ca/ineed/tofindadoctor/pages/directory.aspx

- Last revised was June 2022, long ago
- Lots of outdated data, such as:
- Some of them don't list the clinic name, just address. How is there a doctor without a clinic?
- One doctor listed is a cosmetic doctor, not a family doctor
- One doctor listed under a clinic that has closed down long ago, "Prime Urgent Care clinic"
- Another doctor listed without a clinic name, and at the address, it got replaced by a physio clinic

## Health Care Connect

https://www.health.gov.on.ca/en/ms/healthcareconnect/pro/

Ontario System. Unattached patients can call or go online to [ontario.ca/healthcareconnect](https://www.ontario.ca/page/find-family-doctor-or-nurse-practitioner) to register with the program. To register patients must have a valid OHIP card and complete a health questionnaire to determine their need for family health care services. Participants are assigned to a Care Connector. Care Connectors are nurses employed by Home and Community Care Support Services Organizations. Once an available provider is found, Health Care Connect will give the patient the provider's practice information to schedule their first appointment.

- Bloated way
- Feb 2023: 7 people said they were on the list for 2-5 years: https://www.reddit.com/r/ottawa/comments/110f0y7/can_someone_help_me_with_this_health_care_connect/