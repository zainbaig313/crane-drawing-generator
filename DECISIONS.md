Q1  Who is the user, and what do they need?
ANs :the is  Modern Crane Co or any Crane design engineer who need a simple applicationn that can genrate a 2D drawing of single grider crane with front elevation drawing with labelled component(the type can be different base on the user need.for easy and quick submission i have use single grider crane) instead they manually open the CAD software and draw every desgin from scrach .And drwaing each line manually .the user will type simple paramter for the crane and it will genrate a live SVG desgin for them .

------------------------------------------------------------------------------------------------------------------------------
Q2.. What did you assume (crane type, inputs, units, ranges), and why?

i didnot assume anything since i have 0 knowlege of cranes instead i have search of overhead cranes type and ask chatgpt about it. after than i ask chatgpt what are the minimal input a engineer use to draw a crane desgin .and the units and inputs and ranges were completely base on the chatgpt response.Than i search for the crane type that will be most easy enough to genrate in 2D by python .I selected the front elevation after seeing the sample image and tough it would be easy to genrate a front view for the given time line and its also provide a good view of the main crane components, including the girder, end carriages, trolley, hook block, and runway rails.

-----------------------------------------------------------------------------------------------------------------------------
Q.3 Where did each formula or rule come from, and how sure are you?
Ans. As of having zero knowledge about the cranes and their desgin fromulas. the formulas are completely genrate by the ai model during project creation upon my promt . how ever i have verified it through little bit search and i think they are fine however i am not 100% sure about it since it can contain mistakes . for example doing a little research about the formula determining the number of vertical internal stiffeners . i have give the screen shot to the google and got this reponse stating 

AI genrated text :-
1. Rounding Down Violates the 2,500 mm Limit: Because it uses the floor function (|span/2500|), the actual spacing between internal stiffeners will often exceed 2,500 mm.
	• Example: For a 14,500 mm (14.5 m) span,  |14500 / 2500|  = 5  internal stiffeners. Five internal stiffeners divide the girder into 5 + 1 = 6 bays, making each bay 14500/6 = 2,417 mm (okay).
	• However, if the formula counts all stiffeners including the 2 end-bearing stiffeners, 5 total stiffeners only creates 5 - 1 = 4 bays, giving a spacing of 14500/4 =3,625mm which breaks the 2,500 mm rule.
2. Hard Cap of 12: Capping at 12 means any crane spanning longer than 32.5 m (for internal stiffeners) or 30 m (if end stiffeners are included) will automatically exceed the 2,500 mm spacing limit.


by reading this i can say the formulas are correct to some points how ever they can be made better if  i will bee getting direct inpput from a qualified person.


------------------------------------------------------------------------------------------------------------------------------
4. What did you leave out on purpose?
Ans. What i left on purpose are multiple cranes type and mutliple drawing views and use minimal parameter i am sure engineer use mulitple and more parameters while drawing a crane for example how much load it can carry etc.and for the webiste i have leave the role base authentication since the assigment was focused on genrate a drawing of the user inputs  . i have also use only svg and didnot include the CAD extension files by which a user can download and open a files in the CAD and edit it beacuse i Dont have CAD and i am not fimiliary with it using .



----------------------------------------------------------------------------------------------------------------------------
5. What three questions would you ask our engineers?
Ans. The very first question i would ask them would be how many paramters should a user enter and what thing should be calcualted by it self and what should be validation . also i would like to know which engineers fromulas or standard their company use while drawing a crane desgin . the little bit of reasearch i did shows  there are many enginner standards.but  i havenot dive in details of them .also one more thing i want to ask them is how much detail they want in the drawing for example the  sample you have shared has many detail lines and everthing while the image genrated by my python code is very simple, and gernal .

--------------------------------------------------------------------------------------------------------------------------
6. What would you do with another week?

ANS :  oh i will  definitely learn about few formulas and try to learn what more paramters and specification enginner use to draw such a complicated drawings .and what happen if things goes wrong while drawign the example a parameter that seems fine but fail when a crane is manufactured . i will also add the login and role base access so each user has his own drawings . I will also add the genration of CAD files so user can open the files later in CAD. i will also add 1-2 more views or maybe crane types .



