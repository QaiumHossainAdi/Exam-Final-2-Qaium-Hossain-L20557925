# CastCheck AI — Presentation Speech Notes (English + বাংলা)

About 7–8 minutes. Demo data: **Road pavement** with `road_pavement.csv` uploaded in Project Settings.
Each part has the English text first, then the Bengali. **[Show: …]** tells you what to click.

---

## 1. Opening — the problem (≈45 s)

**English**
Good morning everyone. Concrete is the most used construction material in the world, but its quality
is checked late. We pour it today, and we only learn its real strength after 28 days. By then more
concrete has been poured on top, forms are removed and loads are applied. A small mistake on site, such
as extra water in a truck, can become a very expensive repair. My project, **CastCheck AI**, helps
engineers find these problems earlier, explain the cause, and decide the next step.

**বাংলা**
সবাইকে শুভেচ্ছা। কংক্রিট পৃথিবীতে সবচেয়ে বেশি ব্যবহৃত নির্মাণ উপকরণ, কিন্তু এর মান যাচাই হয় অনেক দেরিতে।
আজ আমরা কংক্রিট ঢালি, আর এর আসল শক্তি জানতে পারি ২৮ দিন পরে। ততদিনে এর উপর আরও কংক্রিট ঢালা হয়ে যায়,
ফর্মওয়ার্ক খুলে ফেলা হয়, লোড দেওয়া হয়। সাইটে ছোট একটি ভুল, যেমন ট্রাকে বাড়তি পানি মেশানো, পরে অনেক
ব্যয়বহুল মেরামতে পরিণত হতে পারে। আমার প্রজেক্ট **CastCheck AI** ইঞ্জিনিয়ারদের এই সমস্যাগুলো আগেভাগে
খুঁজে বের করতে, কারণ ব্যাখ্যা করতে এবং পরবর্তী পদক্ষেপ ঠিক করতে সাহায্য করে।

---

## 2. What CastCheck AI does (≈30 s)

**[Show: Overview — the 5 steps at the top]**

**English**
The app follows the full life of concrete in five steps: **Design, Optimize, Accept, Warn and Diagnose.**
It designs the mix with ACI 211.1, finds cheaper and lower-carbon mixes, checks lab results with the
ACI 318 building code, warns early from 7-day tests, and diagnoses the likely cause of a low result.

**বাংলা**
অ্যাপটি কংক্রিটের পুরো জীবনচক্র পাঁচটি ধাপে অনুসরণ করে: **Design, Optimize, Accept, Warn এবং Diagnose।**
এটি ACI 211.1 অনুযায়ী মিক্স ডিজাইন করে, কম খরচ ও কম কার্বনের মিক্স খুঁজে দেয়, ACI 318 বিল্ডিং কোড অনুযায়ী
ল্যাব রেজাল্ট যাচাই করে, ৭ দিনের টেস্ট থেকে আগাম সতর্কতা দেয়, এবং কম শক্তির সম্ভাব্য কারণ নির্ণয় করে।

---

## 3. Project setup and data (≈40 s)

**[Show: top bar → Application = Road pavement; then Project Settings → Pour Log Data]**

**English**
First I choose the type of project. For a road pavement the app automatically sets the rules: specified
strength f'c of 4,500 psi, maximum water-cement ratio 0.45, and exposure class F2 for freezing and
thawing. A bridge deck with deicing salt gets stricter rules. Then I upload the pour log — one row per
pour with cylinder strengths, slump, air, curing temperature and delivery time. The data you see today
is realistic **demo data**, not a real project.

**বাংলা**
প্রথমে আমি প্রজেক্টের ধরন বেছে নিই। রোড পেভমেন্টের জন্য অ্যাপ স্বয়ংক্রিয়ভাবে নিয়মগুলো ঠিক করে দেয়: নির্ধারিত
শক্তি f'c ৪,৫০০ psi, সর্বোচ্চ পানি-সিমেন্ট অনুপাত ০.৪৫, আর জমাট-গলন (freeze-thaw) এর জন্য exposure class F2।
ডিআইসিং লবণযুক্ত ব্রিজ ডেকের জন্য নিয়ম আরও কঠোর। এরপর আমি pour log আপলোড করি — প্রতিটি ঢালাইয়ের জন্য
এক সারি, যেখানে সিলিন্ডারের শক্তি, স্লাম্প, এয়ার, কিউরিং তাপমাত্রা ও ডেলিভারির সময় থাকে। আজকের ডেটা বাস্তবসম্মত
**ডেমো ডেটা**, কোনো আসল প্রজেক্টের নয়।

---

## 4. Lab results — Strength Control Chart (≈60 s)

**[Show: Overview → Strength Control Chart, or 3. Lab Results]**

**English**
Each blue dot is one pour's 28-day strength. The white line is the average of the last three tests.
ACI 318 has two rules: the **average of three tests must stay above f'c** — the green line at 4,500 psi —
and **no single test may fall below 4,000 psi** — the red line. Three pours fail the individual limit:
P05, P10 and P13, shown in red. P12 is orange: the pour itself is fine, but P10 pulled the three-test
average below 4,500. Notice also that the white line drops in June — the whole job is getting weaker,
not just one pour.

**বাংলা**
প্রতিটি নীল বিন্দু একটি ঢালাইয়ের ২৮ দিনের শক্তি। সাদা লাইনটি শেষ তিনটি টেস্টের গড়। ACI 318-এ দুটি নিয়ম আছে:
**তিনটি টেস্টের গড় f'c এর উপরে থাকতে হবে** — সবুজ লাইন, ৪,৫০০ psi — এবং **কোনো একক টেস্ট ৪,০০০ psi এর নিচে
যেতে পারবে না** — লাল লাইন। তিনটি ঢালাই একক সীমা পার করতে পারেনি: P05, P10 এবং P13, লাল রঙে দেখানো।
P12 কমলা: ঢালাইটি নিজে ঠিক আছে, কিন্তু P10 এর কারণে তিন টেস্টের গড় ৪,৫০০ এর নিচে নেমে গেছে। আরও লক্ষ্য
করুন, জুন মাসে সাদা লাইনটি নিচে নামছে — শুধু একটি ঢালাই নয়, পুরো কাজের মান কমছে।

---

## 5. Early warning (≈40 s)

**[Show: 4. Early Warning]**

**English**
Normally we wait 28 days to know if concrete passes. CastCheck estimates the 28-day strength from the
7-day test and gives the **probability of failure**. Pour P16 only has its 7-day result, and the app
already says it is likely to fail. That gives us **three weeks** to act: keep the props in place, delay
loading, and fix the mix before the next pour.

**বাংলা**
সাধারণত কংক্রিট পাস করবে কিনা জানতে আমরা ২৮ দিন অপেক্ষা করি। CastCheck ৭ দিনের টেস্ট থেকে ২৮ দিনের শক্তি
অনুমান করে এবং **ফেল করার সম্ভাবনা** দেখায়। P16 এর শুধু ৭ দিনের রেজাল্ট আছে, তবুও অ্যাপ এখনই বলছে এটি সম্ভবত
ফেল করবে। এতে আমরা **তিন সপ্তাহ** সময় পাই ব্যবস্থা নেওয়ার জন্য: প্রপ বা সাপোর্ট রেখে দেওয়া, লোড দেরিতে দেওয়া,
এবং পরের ঢালাইয়ের আগে মিক্স ঠিক করা।

---

## 6. Diagnose — why did it fail? (≈50 s)

**[Show: 5. Investigate → choose P10, then P05]**

**English**
When a test fails, the app reads the evidence from the site record and ranks the likely causes. For P10,
the slump was much higher than designed and the truck took over 90 minutes, so the most likely cause is
**water added on site, 93 percent**. For P05 the air content was too high, so the cause is **high air**.
Each cause comes with the next step — for example, check delivery tickets and take cores. The app does
not just say "fail"; it explains **why** and **what to do**.

**বাংলা**
কোনো টেস্ট ফেল করলে অ্যাপ সাইটের রেকর্ড থেকে প্রমাণ পড়ে এবং সম্ভাব্য কারণগুলো ক্রমানুসারে সাজায়। P10 এর ক্ষেত্রে
স্লাম্প ডিজাইনের চেয়ে অনেক বেশি ছিল এবং ট্রাক ৯০ মিনিটের বেশি সময় নিয়েছে, তাই সবচেয়ে সম্ভাব্য কারণ **সাইটে পানি
মেশানো, ৯৩ শতাংশ**। P05 এ এয়ার কনটেন্ট বেশি ছিল, তাই কারণ **অতিরিক্ত এয়ার**। প্রতিটি কারণের সাথে পরবর্তী পদক্ষেপও
দেওয়া থাকে — যেমন ডেলিভারি টিকেট যাচাই করা এবং কোর টেস্ট করা। অ্যাপ শুধু "ফেল" বলে না; এটি বলে **কেন** এবং
**কী করতে হবে**।

---

## 7. Bridge Digital Twin (≈40 s)

**[Show: Bridge Digital Twin → click Section 2; scroll to the heatmap]**

**English**
This is a map of the project. Each block is one section, colored by its worst result. Section 1 is green
— all pours passed. Sections 2, 3 and 4 are red. When I click Section 2, I see its four pours and the open
investigation for P05. The heatmap below shows every pour in the order it was placed. So the twin answers
**where** the problem is, and the heatmap answers **which pour** caused it.

**বাংলা**
এটি প্রজেক্টের একটি ম্যাপ। প্রতিটি ব্লক একটি সেকশন, যার রং তার সবচেয়ে খারাপ ফলাফল অনুযায়ী। সেকশন ১ সবুজ — সব
ঢালাই পাস করেছে। সেকশন ২, ৩ ও ৪ লাল। সেকশন ২ এ ক্লিক করলে এর চারটি ঢালাই এবং P05 এর চলমান তদন্ত দেখা যায়।
নিচের হিটম্যাপে প্রতিটি ঢালাই সময়ের ক্রমে দেখানো হয়েছে। অর্থাৎ ডিজিটাল টুইন বলে সমস্যা **কোথায়**, আর হিটম্যাপ বলে
**কোন ঢালাই** এর জন্য দায়ী।

---

## 8. Batch Deviation Check (≈30 s)

**[Show: Batch Deviation Check]**

**English**
Every truck comes with a batch ticket. The app compares it with the approved mix using the ASTM C94
tolerances: cement plus or minus 1 percent, water 3 percent, aggregates 2 percent. Here three of twelve
tickets are outside tolerance — for example P07, where 25 gallons of water were added on site. This check
can stop a bad truck **at the gate, before the concrete is poured.**

**বাংলা**
প্রতিটি ট্রাকের সাথে একটি ব্যাচ টিকেট আসে। অ্যাপ এটিকে অনুমোদিত মিক্সের সাথে ASTM C94 সহনসীমা দিয়ে তুলনা করে:
সিমেন্ট ±১ শতাংশ, পানি ৩ শতাংশ, অ্যাগ্রিগেট ২ শতাংশ। এখানে বারোটির মধ্যে তিনটি টিকেট সীমার বাইরে — যেমন P07,
যেখানে সাইটে ২৫ গ্যালন পানি মেশানো হয়েছে। এই যাচাই খারাপ ট্রাককে **ঢালাইয়ের আগেই, গেটেই আটকাতে পারে।**

---

## 9. Optimize Mix — cost and carbon (≈45 s)

**[Show: 2. Optimize Mix]**

**English**
Cement production causes most of concrete's carbon emissions. The optimizer replaces part of the cement
with slag, a steel-industry by-product, and uses a little superplasticizer to reduce water — while still
meeting the strength and durability rules. Compared with the standard ACI mix at 99 dollars and 390
kilograms of CO2 per cubic meter, the lowest-carbon mix costs about the same and cuts CO2 by **52
percent**. These are candidate mixes; a lab trial batch is still required.

**বাংলা**
কংক্রিটের বেশিরভাগ কার্বন নিঃসরণ হয় সিমেন্ট উৎপাদন থেকে। অপটিমাইজার সিমেন্টের একটি অংশ স্ল্যাগ দিয়ে প্রতিস্থাপন
করে — যা ইস্পাত শিল্পের উপজাত — এবং পানি কমাতে সামান্য সুপারপ্লাস্টিসাইজার ব্যবহার করে, তবুও শক্তি ও স্থায়িত্বের
সব নিয়ম মেনে চলে। স্ট্যান্ডার্ড ACI মিক্সের খরচ প্রতি ঘনমিটারে ৯৯ ডলার এবং ৩৯০ কেজি CO2; সবচেয়ে কম কার্বনের মিক্সে
খরচ প্রায় একই, কিন্তু CO2 কমে **৫২ শতাংশ**। এগুলো প্রস্তাবিত মিক্স; ব্যবহারের আগে ল্যাবে ট্রায়াল ব্যাচ করা জরুরি।

---

## 10. Trust — Model Validation (≈30 s)

**[Show: 6. Model Validation]**

**English**
An AI model is only reliable inside the data it learned from. The app checks every mix against the range
of the UCI dataset of 1,030 real lab mixes. Here the standard mix has slightly more coarse aggregate than
the dataset contains, so it is marked red: **extrapolation**. The app tells the user when to trust a
prediction less — that is responsible AI.

**বাংলা**
একটি AI মডেল কেবল সেই ডেটার সীমার মধ্যেই নির্ভরযোগ্য, যেটি থেকে এটি শিখেছে। অ্যাপ প্রতিটি মিক্সকে UCI ডেটাসেটের
১,০৩০টি আসল ল্যাব মিক্সের সীমার সাথে মিলিয়ে দেখে। এখানে স্ট্যান্ডার্ড মিক্সে ডেটাসেটের চেয়ে সামান্য বেশি কোর্স
অ্যাগ্রিগেট আছে, তাই এটি লাল চিহ্নিত: **extrapolation**। কখন একটি পূর্বাভাসে কম ভরসা করতে হবে, অ্যাপ তা ব্যবহারকারীকে
জানিয়ে দেয় — এটাই দায়িত্বশীল AI।

---

## 11. Why it matters — real incidents (≈40 s)

**English**
These problems are real. In **1978 at Willow Island**, West Virginia, a cooling tower collapsed during
construction and 51 workers died; the investigation found loads were placed on concrete that was not yet
strong enough. In **New York**, a testing lab was convicted in 2010 of faking concrete strength reports on
more than 100 projects. On Boston's **Big Dig**, the supplier paid 50 million dollars after thousands of
truckloads did not meet specification. CastCheck AI is built to flag exactly these kinds of problems
early. It does not claim it would have prevented them.

**বাংলা**
এই সমস্যাগুলো বাস্তব। **১৯৭৮ সালে যুক্তরাষ্ট্রের ওয়েস্ট ভার্জিনিয়ার উইলো আইল্যান্ডে** নির্মাণাধীন একটি কুলিং টাওয়ার
ধসে ৫১ জন শ্রমিক মারা যান; তদন্তে দেখা যায়, যথেষ্ট শক্তি অর্জনের আগেই কংক্রিটের উপর লোড দেওয়া হয়েছিল। **নিউ ইয়র্কে**
২০১০ সালে একটি টেস্টিং ল্যাব ১০০টিরও বেশি প্রজেক্টে কংক্রিটের শক্তির ভুয়া রিপোর্ট দেওয়ার দায়ে দোষী সাব্যস্ত হয়।
বোস্টনের **বিগ ডিগ** প্রজেক্টে হাজার হাজার ট্রাক কংক্রিট স্পেসিফিকেশন পূরণ না করায় সরবরাহকারীকে ৫০ মিলিয়ন ডলার দিতে
হয়। CastCheck AI ঠিক এই ধরনের সমস্যাগুলো আগেভাগে চিহ্নিত করার জন্য তৈরি। এটি দাবি করে না যে এগুলো ঠেকাতে পারত।

---

## 12. Limits and closing (≈40 s)

**English**
To be clear about the limits: today's data is synthetic, prices and carbon factors are assumed values,
and optimized mixes need lab trials. The app supports the engineer — it does not replace the engineer,
and the project specification always governs. In one line: **CastCheck AI turns a 28-day surprise into a
7-day warning, explains the cause, and helps build stronger, cheaper and greener concrete.** Thank you —
I am happy to take questions.

**বাংলা**
সীমাবদ্ধতাগুলো স্পষ্ট করে বলি: আজকের ডেটা কৃত্রিম, দাম ও কার্বনের মানগুলো অনুমিত, এবং অপটিমাইজড মিক্সের ল্যাব ট্রায়াল
প্রয়োজন। অ্যাপটি ইঞ্জিনিয়ারকে সহায়তা করে — ইঞ্জিনিয়ারের বিকল্প নয়, এবং প্রজেক্ট স্পেসিফিকেশনই সবসময় চূড়ান্ত।
এক কথায়: **CastCheck AI ২৮ দিনের অপ্রত্যাশিত ফলাফলকে ৭ দিনের আগাম সতর্কতায় পরিণত করে, কারণ ব্যাখ্যা করে, এবং আরও
মজবুত, সাশ্রয়ী ও পরিবেশবান্ধব কংক্রিট তৈরিতে সাহায্য করে।** ধন্যবাদ — আপনাদের প্রশ্নের অপেক্ষায় রইলাম।

---

## Likely questions — short answers

| Question | English answer | বাংলা উত্তর |
|---|---|---|
| Is the data real? | No, it is realistic demo data. Real pour logs can be uploaded or typed in. | না, এটি বাস্তবসম্মত ডেমো ডেটা। আসল pour log আপলোড বা টাইপ করে দেওয়া যায়। |
| The concrete is already poured — what is the use? | The 7-day warning comes 3 weeks earlier: protect the structure and fix the next pours. Batch check works before pouring. | ৭ দিনের সতর্কতা তিন সপ্তাহ আগে আসে: কাঠামো রক্ষা ও পরের ঢালাই ঠিক করা যায়। ব্যাচ চেক ঢালাইয়ের আগেই কাজ করে। |
| How do you fix a failed pour? | Take cores (ACI 318: average ≥ 85% f'c, none < 75%). If cores fail, the engineer checks capacity, then strengthens or replaces. | কোর টেস্ট (ACI 318: গড় ≥ ৮৫% f'c, কোনোটি < ৭৫% নয়)। কোর ফেল করলে ইঞ্জিনিয়ার সক্ষমতা যাচাই করে শক্তিশালী বা প্রতিস্থাপন করেন। |
| How accurate is the diagnosis? | It is a probability ranking from evidence (naive Bayes). The likelihoods are assumptions that can be learned from real cases. | এটি প্রমাণভিত্তিক সম্ভাবনার ক্রম (naive Bayes)। সম্ভাবনার মানগুলো অনুমিত, আসল কেস থেকে শেখানো যায়। |
| Can it replace the engineer? | No. It finds problems early and recommends; the engineer decides. | না। এটি আগেভাগে সমস্যা খুঁজে সুপারিশ করে; সিদ্ধান্ত ইঞ্জিনিয়ারের। |
