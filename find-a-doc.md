Meeting agenda

1.  Discuss Scope: 
	1. Problem: There is a lack of updated information when it comes to family doctors accepting patients (i.e. my doc wasn't on the peel region site). The websites that display this info also have bad UI/UX. They also lack reviews for each doctor. My mom got a serious kidney infection due to her family doctor dismissing her concern of frequent urination.
		1. Related posts of people complaining:
		2. https://www.reddit.com/r/ontario/comments/o5vrrx/finding_a_family_doctor_shouldnt_be_this_hard/
		3. https://www.reddit.com/r/ontario/comments/11sx2he/how_do_i_find_a_family_doctor/
		4. https://www.reddit.com/r/askTO/comments/v4ltuh/family_doctors_accepting_new_patients_in_the/
	2. Audience: Anyone looking for a family doctor.
	3. MVP Solution:
		1. Create an updated list of family doctors in Toronto as well as their gender. Do this by calling all clinics monthly, beginning in Mississauga, asking 2 questions: 
			1. If there are any family doctors accepting patients.
			2. If yes, for every doctor ask their name and gender.
		2. A website to show this data in a intuitive manner. Users just input their address and preferred gender of doctor and it gives them a recommendation. They can also see all available doctors in whatever area they want.
		3. If possible: incorporate a way to see reviews for doctors, post reviews for doctors, and recommend based on reviews
2.  Website Tech Stack
	1. Frontend: Svelte
	2. Backend: May not be needed if we don't save any user data, frontend can directly query supabase
	3. Database: Supabase, easy to use serverless postgres
3. Data Collection Tools:
	1. Twilio to make calls
	2. Possibly chatgpt to direct conversation
	3. Speech to text: OpenAI Whisper for 
	4. Text to speech: google cloud or wellsaidlabs with Cameron S. name
	5. Can run these python script(s) locally
	6. Can store recordings in google drive
4. Tools:
	1. Excalidraw to show conversation flow
5.  Discuss following meeting regulations and schedule
	1. Meet Saturday, Sunday, Tuesday, Thursday, 8-10pm

What we need


up to date clinic info:
- location
- name
- phone number
- opening times
- get from google maps API
managing phone calls:
- speechify for text to speed
- google cloud as well
- first use basic if statements to get through menu and conversate
- possibly use chat gpt 3.5
- 
recoridng and displaying data