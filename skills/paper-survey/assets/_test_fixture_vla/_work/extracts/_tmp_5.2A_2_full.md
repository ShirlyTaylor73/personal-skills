--- Page 1 ---
PaLM-E: An Embodied Multimodal Language Model
DannyDriess12 FeiXia1 MehdiS.M.Sajjadi3 CoreyLynch1 AakankshaChowdhery3
BrianIchter1 AyzaanWahid1 JonathanTompson1 QuanVuong1 TianheYu1 WenlongHuang1
YevgenChebotar1 PierrPeROSMPTe:rmanet1 DanielDuckworth3 SergeyLevine1 VincentVanhoucke1
Q: How can embodied language PROMPT:
KarolHausman1 MarcTmoodeulss bseaneifnitt r2obotKs? l aA:usGreff3 An LdangyuaZge emondegls1 whiIchg uondrerMstanod rdatch3 PeteFlorence1
PREDICTION: robot sensor data can
Embodied language models can PREDICTION:
1Rb l e eon a e rbf n i ot l atr nio gcb u o ast g s ea b ity n Ga a l l moo o w roi e n gg n alt teh u e r m a l 2t oT UBerli l nb a e n g u u s a e g 3d e Gt d o e o s g c oe r n i ge p r t la i et o e n s Rn a o et f u sr t a h el e a rch
way. robot's environment.
https://palm-e.github.io
Mobile Manipulation PaLM-E: An Embodied Multimodal Language Model Task and Motion Planning
Given <emb> … <img> Q: How to grasp blue block? A: First, grasp yellow block Given <emb> Q: How
to grasp blue block?
? ViT A: First grasp yellow
block and place it on
… … the table, then grasp
the blue block.
Large Language Model (PaLM)
Human: Bring me the rice chips from the Tabletop Manipulation
drawer. Robot: 1. Go to the drawers, 2. Open … …
Given <img> Task: Sort
top drawer. I see <img>. 3. Pick the green rice
colors into corners.
chip bag from the drawer and place it on the C o n t r o l A: First, grasp yellow block and … Step 1. Push the green
counter.
star to the bottom left. Scene Understanding
Visual Q&A, Captioning … Describe the Language Only Tasks S c t ir e c p le 2 t . o P t u h s e h g th re e e g n r e st e a n r . Given <img1> and
Given <img>. Q: What’s in the following <img>: Here is a Haiku about <img2> Q: what
i A m : a 🍏 ge 🍌 ? A 🍇 ns 🍐 we 🍑 r in 🍈 e 🍒 mo . jis. A ov d e o r g a j h u u m rd p l i e n g a t a e Em m b b o o d d i i e e d d l l a a n n g g u u a a g g e e models: Q Q : : W Mi h a a m t i i s B 3 e 7 a 2 c h x b 18 o ? r d A e : r 6 s 6 w 96 h . i ch ocean? A: Atlantic. TB T D BD d up id ? t A h : e T r h o e b ot pick
dog show. models are the future of Language models trained on robot sensor data can multi-grain chips.
natural language be used to guide a robot’s actions.
Figure 1: PaLM-E is a single general-purpose multimodal language model for embodied reasoning tasks, visual-language tasks, Visual Q&A
andlanguagetasks. PaLM-Etransfersknowledgefromvisual-languagedomainsintoembodiedreasoning–fromrobotplanningin Given <img1> Q:
environmentswithcomplexdynamicsandphysicalconstraints,toansweringquestionsabouttheobservableworld.PaLM-Eoperateson what days might I
multimodalsentences,i.e.sequencesoftokenswhereinputsfromarbitrarymodalities(e.g.images,neural3Drepresentations,orstates,in TBD most commonly go
to this building?
greenandblue)areinsertedalongsidetexttokens(inorange)asinputtoanLLM,trainedend-to-end.
A: Sunday.
Abstract 1.Introduction
Largelanguagemodels(LLMs)demonstratestrongreason-
Largelanguagemodelshavebeendemonstratedtoperform
ingcapabilitiesacrossvariousdomains,includingdialogue
complextasks. However,enablinggeneralinferenceinthe
(Glaeseetal.,2022;Thoppilanetal.,2022),step-by-step
realworld,e.g.forroboticsproblems,raisesthechallenge
reasoning(Weietal.,2022;Kojimaetal.,2022),mathprob-
ofgrounding. Weproposeembodiedlanguagemodelstodi-
lemsolving(Lewkowyczetal.,2022;Poluetal.,2022),and
rectlyincorporatereal-worldcontinuoussensormodalities
codewriting(Chenetal.,2021a). However,alimitationof
into language models and thereby establish the link be-
suchmodelsforinferenceintherealworldistheissueof
tweenwordsandpercepts. Inputtoourembodiedlanguage
grounding: while training LLMs on massive textual data
modelaremulti-modalsentencesthatinterleavevisual,con-
mayleadtorepresentationsthatrelatetoourphysicalworld,
tinuousstateestimation,andtextualinputencodings. We
connectingthoserepresentationstoreal-worldvisualand
traintheseencodingsend-to-end,inconjunctionwithapre-
physical sensor modalities is essential to solving a wider
trainedlargelanguagemodel,formultipleembodiedtasks
rangeofgroundedreal-worldproblemsincomputervision
includingsequentialroboticmanipulationplanning,visual
androbotics(Tellexetal.,2020). Previouswork(Ahnetal.,
questionanswering,andcaptioning. Ourevaluationsshow
2022)interfacestheoutputofLLMswithlearnedrobotic
thatPaLM-E,asinglelargeembodiedmultimodalmodel,
policiesandaffordancefunctionstomakedecisions,butis
canaddressavarietyofembodiedreasoningtasks,froma
limitedinthattheLLMitselfisonlyprovidedwithtextual
varietyofobservationmodalities,onmultipleembodiments,
input,whichisinsufficientformanytaskswherethegeo-
and further, exhibits positive transfer: the model benefits
metricconfigurationofthesceneisimportant. Further,in
fromdiversejointtrainingacrossinternet-scalelanguage,
ourexperimentsweshowthatcurrentstate-of-the-artvisual-
vision, and visual-language domains. Our largest model,
languagemodelstrainedontypicalvision-languagetasks
PaLM-E-562Bwith562Bparameters,inadditiontobeing
suchasvisual-question-answering(VQA)cannotdirectly
trained on robotics tasks, is a visual-language generalist
solveroboticreasoningtasks.
withstate-of-the-artperformanceonOK-VQA,andretains
generalistlanguagecapabilitieswithincreasingscale. Inthispaperweproposeembodiedlanguagemodels,which
3202
raM
6
]GL.sc[
1v87330.3032:viXra

--- Page 2 ---
PaLM-E:AnEmbodiedMultimodalLanguageModel
Visually-conditioned Jokes + Few-shot prompting Robot Visual Perception, Dialogue, and Planning Robot: I am a robot operating in a kitchen. Given
<img>, what do I see? a bowl of eggs, a bowl of
I see (image omitted). Description: A cow flour, and a bowl of sugar.. and a spatula.. and a spoon.. and a bag of flour.. and a bag of
sitting on a rug. Joke: Why is the cow sugar. When a human asks me to do a task, I will respond with the sequence of actions
sitting on a rug? Because it wants to be a I would do to accomplish the task with only the items I see. Human: Use all of the
cow-ch! … I see <img>. Description: a ingredients you see to make a cake batter. 1. crack egg. 2. put egg in bowl. 3. put flour
donkey is carrying a dog, cat, and rooster. in bowl. 4. put sugar in bowl. 5. mix. 6. put in pan. 7. bake. 8. eat. 9. clean up.
Joke: what do you call a donkey with a
rooster on his back. A rooster booster. Physical Prediction Spatial Grounding Given <img> . Q: What
Given <img>. Q: If a flavor is the doughnut
Zero-shot Multimodal Chain-of-Thought Robot Initiative robot wanted to be Given <img> . on the right? Strawberry.. Q:
useful here, what Q: What will What flavor is the doughnut
Given <img>. Q: Can I go down steps should it take? the robot do on the left? A blueberry.
this street on a bicycle, yes or A: clean table..pick next? A: fall.
no? A: Let’s think step by step. up trash.. pick up Photo 1: <img1>. Photo 2: <img2>. Q: What is in Photo 1
1. do not enter. 2. except chairs.. wipe chairs.. but NOT in Photo 2? A: sunglasses.
bicycles. 3. do not entry except put chairs down. Photo 1: <img1>. Photo 2: <img2>. Q: What is in Photo 1
bicycles. 4. yes. Zero-shot: Multi-image Relationships but NOT in Photo 2? A: Let’s think step by step and
explain. Photo 1 has sunglasses on top of folded
Given <img>. Q: How many Q: Where is clothes. Photo 2 does not have sunglasses on top of
championship rings did the player <img1> in this folded clothes. Therefore, sunglasses are in Photo 1 but
on the left win in his career A: Let’s scene <img2>? A: not in Photo 2.
think step by step. 1. kobe bryant is a stove top with a
on the left. 2. kobe bryant has won pot on it. End-to-End Egocentric Q&A, Dialogue
5 championship rings.
Given <img>. Q: Who are the two teams playing in this OCR-free Math Reasoning Given <img> . P P h h o o t t o o 1 2 , , a a t t 1 1 0 2 : : 3 4 0 5 a p m m : : < < i i m m g g 1 2 > > . .
photo, and which was the last to win a championship, and Q: I am getting just two Photo 3, at 3:45 pm: <img3>.
which year did they win, and who was their star player that custom pizza for me and my Q: I forget, what did I have for
year? A: Let's think step by step. 1. team in white is new friend. How much should I lunch, and what time was it? A:
york knick. 2. team in green is boston celtic. 3. last to win championship was pay in total? A: Let's think Let’s think step by step.
boston celtic. 4. year was 2008. 5. star player was paul pierce. 6. i am not step by step. 1st step: 2 1. you had a sandwich for lunch.
sure if this is correct. i am not basketball fan. i just google it. custom pizzas. 2nd step: 2 x 2. it was 12:45 pm.
$9.99. 3rd step: $19.98.
Figure2: PaLM-E-562Bcandozero-shotmultimodalchain-of-thoughtreasoning,cantellvisually-conditionedjokesgivenanimage,and
demonstratesanarrayofrobot-relevantmultimodal-informedcapabilitiesincludingperception,visually-groundeddialogue,andplanning.
PaLM-Ealsogeneralizes,zero-shot,tomulti-imagepromptsdespiteonlybeingtrainedonsingle-imageprompts. PaLM-Ecanalso
performmathgivenanimagewithtextually-interleavedhandwrittennumbers.Inaddition,themodelcanperform,zero-shot,questionand
answeringontemporally-annotatedegocentricvision,similartowhatwasshownin(Zengetal.,2022)butend-to-endallinonemodel.
directlyincorporatecontinuousinputsfromsensormodali- efficiency for robotics tasks,Phey.sgic.asl iRgenasiofincinagntlyGiivnecn r<eimags>i .n Qg:
tiesofanembodiedagentandtherebyenablethelanguage learningsuccessfromhandfulsoftrainingexaWmhpichl eosf t,heasne d
Assistive Robotics objects is best for
modelitself tomakemoregroundedinferencesforsequen- evendemonstratingone-shotorzero-shotgenercalilmizbiangti uopn higtho?
Given <img> .What is the human trying to tialdecisionmakingintherealworld.Inputssuchasimages novelcombinationsofobjectsorunseenobjectsA.: ladder.
do and what can the robot do to help?
A: reach cookie. robot could get cookie. andstateestimatesareembeddedintothesamelatentembed-
WescalePaLM-Eupto562Bparameters,integratingthe
dingaslanguagetokensandprocessedbytheself-attention
540B PaLM (Chowdhery et al., 2022) LLM and the 22B
layersofaTransformer-basedLLMinthesamewayastext.
VisionTransformer(ViT)(Dehghanietal.,2023)into,to
We start from a pre-trained LLM in which we inject the
ourknowledge,thelargestvision-languagemodelcurrently
continuousinputsthroughanencoder. Theseencodersare
reported. PaLM-E-562B achieves state-of-the-art perfor-
trainedend-to-endtooutputsequentialdecisionsintermsof
manceontheOK-VQA(Marinoetal.,2019)benchmark,
naturaltextthatcanbeinterpretedbytheembodiedagent
withoutrelyingontask-specificfinetuning. Althoughnot
byconditioninglow-levelpoliciesorgiveananswertoan
thefocusofourexperimentation,wealsofind(Fig.2)that
embodied question. We evaluate the approach in a vari-
PaLM-E-562Bexhibitsawidearrayofcapabilitiesinclud-
ety of settings, comparing different input representations
ingzero-shotmultimodalchain-of-thought(CoT)reasoning,
(e.g. standard vs. object-centric ViT encodings for visual
few-shotprompting,OCR-freemathreasoning,andmulti-
input), freezing vs. finetuning the language model while
imagereasoning,despitebeingtrainedononlysingle-image
trainingtheencoders,andinvestigatingwhetherco-training
examples. Zero-shotCoT(Kojimaetal.,2022),originallya
onmultipletasksenablestransfer.
language-onlyconcept,hasbeenshownonmultimodaldata
Toinvestigatetheapproach’sbreadth,weevaluateonthree withtask-specificprograms(Zengetal.,2022)buttoour
robotic manipulation domains (two of which are closed- knowledge,notviaanend-to-endmodel.
loopinthereal-world),standardvisual-languagetaskssuch
To summarize our main contributions, we (1) propose
asVQAandimagecaptioning, aswellaslanguagetasks.
anddemonstratethatageneralist, transfer-learned, multi-
Ourresultsindicatethatmulti-tasktrainingimprovesperfor-
embodimentdecision-makingagentcanbetrainedviamix-
mancecomparedtotrainingmodelsonindividualtasks. We
inginembodieddataintothetrainingofamultimodallarge
showthatthistransfer acrosstaskscanleadtohighdata-

--- Page 3 ---
PaLM-E:AnEmbodiedMultimodalLanguageModel
languagemodel. Weshowthat,(2)whilecurrentstate-of- rectlyleveragetheworldknowledgeembeddedinitsparam-
the-artgeneral-purposevisual-languagemodelsout-of-the- eters. Thisenablesnotonlyembodiedreasoningbutalso
box (zero-shot) do not well address embodied reasoning question answering, as demonstrated in our experiments.
problems,itispossibletotrainacompetentgeneral-purpose Amongworksthatoutputactions,perhapsmostsimilaris
visual-language model that is also an efficient embodied theapproachproposedinGato(Reedetal.,2022)which,
reasoner. Instudyinghowtobesttrainsuchmodels,we(3) likePaLM-E,isageneralistmulti-embodimentagent. In
introducenovelarchitecturalideassuchasneuralscenerep- contrast to Gato, we demonstrate positive transfer across
resentationsandentity-labelingmultimodaltokens. Finally, differenttaskswherethemodelbenefitsfromdiversejoint
inadditiontoourfocusonPaLM-Easanembodiedreasoner trainingacrossmultipledomains.
we (4) show that PaLM-E is also a quantitatively compe-
LLMsinembodiedtaskplanning. Therehavebeensev-
tent vision and language generalist, and (5) demonstrate
eralmethodsproposedtoleverageLLMsinembodieddo-
that scaling the language model size enables multimodal
mains. Whilemanyworksfocusonunderstandingnatural
finetuningwithlesscatastrophicforgetting.
languagegoals(Lynch&Sermanet,2020;Shridharetal.,
2022a; Nair et al., 2022; Lynch et al., 2022), fewer con-
2.RelatedWork
sider natural language as a representation for planning –
thefocusofthiswork. LLMscontainvastamountsofin-
General vision-language modeling. Building on suc-
ternalizedknowledgeabouttheworld(Bommasanietal.,
cessesinlargelanguage(Brownetal.,2020;Devlinetal.,
2021),butwithoutgrounding,generatedplansmaybeim-
2018)andvision(Dosovitskiyetal.,2020)models,recent
possible to execute. One line of research has employed
yearshaveseenagrowinginterestinlargevision-language
promptingtoelicitasequenceofinstructionsdirectlyfrom
models(VLMs)(Lietal.,2019;Luetal.,2019;Haoetal.,
anLLMeitherbyleveragingsemanticsimilaritybetweenan
2022;Ganetal.,2022). Unliketheirpredecessors,VLMs
LLM’sgenerationandaneligiblesetofinstructions(Huang
arecapableofsimultaneouslyunderstandingbothimages
etal.,2022b),incorporatingaffordancefunctions(Ahnetal.,
and text, and can be applied to tasks such as visual ques-
2022), visual feedback (Huang et al., 2022c), generating
tion answering (Zhou et al., 2020; Zellers et al., 2021b),
worldmodels(Nottinghametal.,2023;Zellersetal.,2021a),
captioning(Huetal.,2022),opticalcharacterrecognition
planningovergraphsandmaps(Shahetal.,2022;Huang
(Lietal.,2021),andobjectdetection(Chenetal.,2021b).
etal.,2022a),visualexplanations(Wangetal.,2023),pro-
Themethodsbywhichimagesareintegratedvaries. Forex-
gramgeneration(Liangetal.,2022;Singhetal.,2022),or
ample,Alayracetal.(2022)augmentspretrainedlanguage
injectinginformationintotheprompt(Zengetal.,2022). In
modelswithamechanismtodirectlyattendtoasinglecon-
contrast,PaLM-Eistrainedtogenerateplansdirectlywith-
text image. In contrast, PaLM-E represents images and
outrelyingonauxiliarymodelsforgrounding. Thisinturn
textas“multimodalsentences”oflatentvectors,allowing
enablesdirectintegrationoftherichsemanticknowledge
ittoprocessmultipleimagesinaflexiblewaywithinany
storedinpretrainedLLMsintotheplanningprocess.
part of a sentence. More closely related to our work is
Frozen (Tsimpoukelli et al., 2021) where vision encoder Withfewexceptions,theparametersoftheLLMsemployed
parameters are optimized via backpropagation through a inmanyoftheseworksareemployedas-iswithoutfurther
frozen LLM (Lu et al., 2021). Inspired by this work, we training. InLID(Lietal.,2022),thisconstraintisrelaxed
investigate the design in a broader scope by introducing andLLMparametersarefinetunedtoproduceaplanningnet-
alternative input modalities (e.g. neural scene representa- workforgeneratinghigh-levelinstructions. (SL)3 (Sharma
tions),andourproposedapproachempiricallyoutperforms etal.,2021)tacklesthemorechallengingtaskofsimulta-
Frozenbymorethan45%ontheVQAv2benchmark. More neouslyfinetuningtwoLLMs: aplanningnetwork,which
importantlywedemonstratethatPaLM-Eisapplicablenot produceshigh-levelinstructions,andalow-levelpolicynet-
onlytoperceptualbutalsoembodiedtasks. work, which selects actions. With PaLM-E, our interests
aredistinctandcomplementary: weinvestigateageneralist,
Actions-outputmodels. Priorworksfocusoncombining
multi-embodimentmodel,acrossmultiplemodalities.
visionandlanguageinputsinanembodiedsettingwiththe
goalofdirectactionprediction(Guhuretal.,2022;Shridhar
3.PaLM-E:AnEmbodiedMultimodal
etal.,2022b;a;Zhang&Chai,2021;Silvaetal.,2021;Jang
etal.,2022;Nairetal.,2022;Lynchetal.,2022;Brohan LanguageModel
et al., 2022). Among these methods, VIMA (Jiang et al.,
ThemainarchitecturalideaofPaLM-Eistoinjectcontinu-
2022)exploresmultimodalpromptssimilartoPaLM-E.The
ous,embodiedobservationssuchasimages,stateestimates,
role of language is perhaps most aptly described as task
or other sensor modalities into the language embedding
specificationintheseworks. Incontrast,PaLM-Egenerates
spaceofapre-trainedlanguagemodel. Thisisrealizedby
high-level instructions as text; in doing so, the model is
encoding the continuous observations into a sequence of
abletonaturallyconditionuponitsownpredictionsanddi-

--- Page 4 ---
PaLM-E:AnEmbodiedMultimodalLanguageModel
vectorswiththesamedimensionastheembeddingspaceof γ : W → X, i.e.p (w |x )withx = γ(w ) ∈ Rk.
LM l 1:l−1 i i
thelanguagetokens. Thecontinuousinformationishence Themappingγ istypicallyrepresentedasalargeembed-
injected into the language model in an analogous way to dingmatrixofsizek×|W|andtrainedend-to-end. Inour
languagetokens. PaLM-Eisadecoder-onlyLLMthatgen- case,|W|=256000(Chowdheryetal.,2022).
eratestextualcompletionsautoregressivelygivenaprefixor
Multi-modalsentences:injectionofcontinuousobserva-
prompt. WecallourmodelPaLM-E,sinceweusePaLM
tions. Multi-modalinformationsuchasimageobservations
(Chowdheryetal.,2022)asthepre-trainedlanguagemodel,
canbeinjectedintotheLLMbyskippingthediscretetoken
andmakeitEmbodied.
levelanddirectlymappingthecontinuousobservationsinto
The inputs to PaLM-E consist of text and (multiple) con- thelanguageembeddingspaceX. Tothisend,wetrainan
tinuousobservations. Themultimodaltokenscorrespond- encoder φ : O → Xq that maps a (continuous) observa-
ing to these observations are interleaved with the text tionspaceO(refertoSec.4fordetails)intoasequenceof
to form multi-modal sentences. An example of such a q-many vectors in X. These vectors are then interleaved
multi-modal sentence is Q: What happened between withnormalembeddedtexttokenstoformtheprefixforthe
<img 1> and <img 2>?where<img i>representsanem- LLM.Thismeansthateachvectorx intheprefixisformed
i
bedding of an image. The output of PaLM-E is text gen- fromeitherthewordtokenembedderγ oranencoderφ :
i
eratedauto-regressivelybythemodel,whichcouldbean
(cid:40)
answertoaquestion,orasequenceofdecisionsproducedby γ(w ) ifiaistexttoken,or
x = i (3)
PaLM-Eintextualformthatshouldbeexecutedbyarobot. i φ (O ) ificorrespondstoobservationO .
j j i j
WhenPaLM-Eistaskedwithproducingdecisionsorplans,
weassumethatthereexistsalow-levelpolicyorplannerthat NotethatasingleobservationO isusuallyencodedinto
j
cantranslatethesedecisionsintolow-levelactions. Prior multiple embedding vectors. It is possible to interleave
workhasdiscussedavarietyofwaystotrainsuchlow-level different encoders φ at different locations in the prefix
i
policies(Lynch&Sermanet,2020;Brohanetal.,2022),and to combine, e.g., information from different observation
weusethesepriormethodsdirectlywithoutmodification. spaces. Injectingthecontinuousinformationthiswayinto
Inthefollowing,wedescribeourapproachmoreformally. theLLMreusesitsexistingpositionalencodings.Incontrast
to other VLM approaches (e.g, (Chen et al., 2022)), the
Decoder-onlyLLMs. Decoder-onlylargelanguagemodels
observationembeddingsarenotinsertedatfixedpositions,
(LLMs)aregenerativemodelstrainedtopredicttheproba-
butinsteadplaceddynamicallywithinthesurroundingtext.
bilityp(w )ofapieceoftextw =(w ,...,w )that
1:L 1:L 1 L
is represented as a sequence of tokens w i ∈ W. Typical Embodyingtheoutput:PaLM-Einarobotcontrolloop.
neuralarchitecturesrealizethisbyfactorizinginto PaLM-E is a generative model producing text based on
multi-model sentences as input. In order to connect the
L
(cid:89) outputofthemodeltoanembodiment,wedistinguishtwo
p(w )= p (w |w ), (1)
1:L LM l 1:l−1 cases. Ifthetaskcanbeaccomplishedbyoutputtingtext
l=1
only as, e.g., in embodied question answering or scene
wherep isalargetransformernetwork. descriptiontasks, thentheoutputofthemodelisdirectly
LM
consideredtobethesolutionforthetask.
Prefix-decoder-only LLMs. Since the LLM is auto-
regressive, a pre-trained model can be conditioned on a Alternatively,ifPaLM-Eisusedtosolveanembodiedplan-
prefixw withoutthenecessitytochangethearchitecture ningorcontroltask, itgeneratestextthatconditionslow-
1:n
levelcommands. Inparticular,weassumetohaveaccessto
L policiesthatcanperformlow-levelskillsfromsome(small)
(cid:89)
p(w n+1:L |w 1:n )= p LM (w l |w 1:l−1 ). (2) vocabulary,andasuccessfulplanfromPaLM-Emustcon-
l=n+1 sistofasequenceofsuchskills. NotethatPaLM-Emust
determine on its own which skills are available based on
The prefix or prompt w provides the context based on
1:n thetrainingdataandtheprompt,andnoothermechanism
whichtheLLMcontinuestopredictthesubsequenttokens
is used to constrain or filter its outputs. Although these
w . Thisisoftenusedforinferencetosteerthepredic-
n+1:L policiesarelanguageconditioned,theyarenotcapableof
tionsofthemodel. Forexample,thepromptcancontaina
solvinglong-horizontasksortakingincomplexinstructions.
descriptionofthetasktheLLMshouldsolveorexamples
PaLM-Eishenceintegratedintoacontrol-loop,whereits
ofdesiredtextcompletionsforsimilartasks.
predicteddecisionsareexecutedthroughthelow-levelpoli-
Tokenembeddingspace. Thetokensw areelementsofa ciesbyarobot,leadingtonewobservationsbasedonwhich
i
fixedvocabularyWwhichisadiscrete,finitesetcorrespond- PaLM-Eisabletoreplanifnecessary. Inthissense,PaLM-
ingto(sub)wordsinnaturallanguage. Internally,theLLM Ecanbeunderstoodasahigh-levelpolicythatsequences
embedsw intoawordtokenembeddingspaceX ⊂Rk via andcontrolsthelow-levelpolicies.
i

--- Page 5 ---
PaLM-E:AnEmbodiedMultimodalLanguageModel
4.Input&SceneRepresentationsfor tecture (Locatello et al., 2020). Based on SRT (Sajjadi
DifferentSensorModalities et al., 2022b), OSRT learns 3D-centric neural scene rep-
resentationsonin-domaindatathroughanovelviewsyn-
Inthissection,wedescribetheindividualmodalitiesthatwe
thesistask. Itsscenerepresentationsconsistofobjectslots
incorporateintoPaLM-E,andhowwesetuptheirencoders. o = φ¯ (I ) ∈ Rk¯ . We project each of these slots
Weproposedifferentarchitecturalchoicesforeachencoder j OSRT 1:v j
into xj = ψ(φ¯ (I ) ) with an MLP ψ. Note that
φ : O → X to map the corresponding modality into the 1:m OSRT 1:v j
individual objects are always tokenized into multiple em-
languageembeddingspace. Weinvestigatestateestimation
beddingseach,i.e.ψ : Rk¯ → Rm×k forOSRTmapsinto
vectors, Vision Transformers (ViTs) (Dosovitskiy et al.,
m-manyembeddings.
2020;Chenetal.,2022;Ryooetal.,2021)for2Dimage
features, and the 3D-aware Object Scene Representation Entity referrals. For embodied planning tasks, PaLM-E
Transformer(OSRT)(Sajjadietal.,2022a). Inadditionto mustbeabletoreferenceobjectsinitsgeneratedplan. In
encodersthatrepresenttheinputsceneglobally,weconsider many cases, including the majority of our experiments,
object-centricrepresentationsthatfactorobservationsinto objects in a scene can be identified in natural language
tokensthatrepresentindividualobjectsinthescene. by some of their unique properties. However, there
also exist settings where objects are not easily identifi-
Stateestimationvectors. Statevectors,e.g.fromarobot
able by language in few words, e.g. if there are multi-
orastateestimateforobjects,areperhapsthesimplestto
ple blocks on a table of the same color at different loca-
inputintoPaLM-E.Lets∈RS beavectordescribingthe
tions. Forobject-centricrepresentationssuchasOSRT,we
stateoftheobjectsinascene. Forexample,scouldcontain
label the multi-modal tokens corresponding to an object
thepose,size,coloretc.ofthoseobjects. Then,theMLP
in the input prompt as follows: Object 1 is <obj 1>.
φ mapssintothelanguageembeddingspace.
state ... Object j is <obj j>. ThisenablesPaLM-Etoref-
Vision Transformer (ViT). ViT φ˜ ViT (Dosovitskiy et al., erenceobjectsviaspecialtokensoftheformobj j inits
2020) is a transformer architecture mapping an image I generatedoutputsentences. Inthiscase,weassumethatthe
into a number of token embeddings x˜ 1:m = φ˜ ViT (I) ∈ low-levelpoliciesoperateonthesetokensaswell.
Rm×k˜
. Weconsiderseveralvariants,includingthe4billion
5.TrainingRecipes
parametermodelfromChenetal.(2022),whichwereferto
asViT-4B,andasimilar22billionparametermodel,ViT- PaLM-E is trained on a dataset of the form D =
22B(Dehghanietal.,2023),bothofwhichhavebeenpre- (cid:8)(cid:0) Ii ,wi ,n (cid:1)(cid:9)N ,whereeachexampleiconsistsof
trainedonimageclassification. Wefurtherinvestigatethe u -m 1: a u n i yc 1 o :L nt i inu i ous i= o 1 bservationsIi, atextwi , andan
ViTtokenlearnerarchitecture(ViT+TL)(Ryooetal.,2021) i j 1:Li
index n . Despite being a decoder-only model, the text
i
which is trained end-to-end from scratch. Note that the
consistsofaprefixpartuptoindexn thatisformedfrom
dimensionalityk˜oftheViTembeddingsisnotnecessarily i
multi-modalsentences,andthepredictiontarget,whichonly
thesameasthatofthelanguagemodel.Wethereforeproject
containstexttokens. Thelossfunctionisthereforeacross-
eachembeddingintox =φ (I) =ψ(φ˜ (I) )withψ
i ViT i ViT i entropylossaveragedovertheindividualnon-prefixtokens
beingalearnedaffinetransformation. wi . To form the multi-modal sentences within the
ni+1:Li
Object-centricrepresentations. Unlikelanguage, visual model,wehavespecialtokensinthetextthatgetreplaced
inputisnotpre-structuredintomeaningfulentitiesandrela- bytheembeddingvectorsoftheencodersatthelocations
tionships:whileViTmaycapturesemantics,thestructureof in the text of those tokens. We base PaLM-E on the pre-
therepresentationresemblesastaticgridratherthanacol- trained8B,62B,and540BparametervariantsofPaLMas
lectionofobjectinstances. Thisposesachallengebothfor thedecoder-onlyLLMintowhichweinjectthecontinuous
interfacingwithLLMswhichhavebeenpre-trainedonsym- observationsthroughtheinputencoders. Thoseencoders
bols, andforsolvingembodiedreasoningwhichrequires areeitherpre-trainedortrainedfromscratch,seeSec.4. We
interactionwithphysicalobjects. Wethereforealsoexplore refertoan8BLLMcombinedwitha4BViTasPaLM-E-
structuredencodersthataimtoseparatevisualinputsinto 12B,similarlya62BLLM+22BViTasPaLM-E-84B,and
distinctobjectsbeforeinjectingthemintotheLLM.Given 540BLLM+22BViTasPaLM-E-562B.
ground-truthobjectinstancemasksM ,wecandecompose
j VariationwithModelfreezing. Mostofourarchitectures
ViT’srepresentationintoxj
1:m
=φ
ViT
(M
j
◦I)forobjectj. consistofthreeparts,anencoderφ˜,aprojectorψ,andthe
LLMp . WhentrainingPaLM-E,onewayistoupdate
ObjectSceneRepresentationTransformer(OSRT).An LM
theparametersofallthesecomponents. However,LLMs
alternativethatdoesnotrequireground-truthsegmentations
showimpressivereasoningcapabilitiesifsuppliedwitha
isOSRT(Sajjadietal.,2022a): ratherthanrelyingonex-
suitableprompt(Weietal.,2022).Therefore,weinvestigate
ternalknowledgeaboutobjects,theyarediscoveredinan
whetheritispossibletofreezetheLLMandtojusttrainthe
unsupervised way through inductive biases in the archi-

--- Page 6 ---
PaLM-E:AnEmbodiedMultimodalLanguageModel
inputencoders,andifso,howdifferent-modalityencoders 100%
compare. Inthiscase,theencoderhastoproduceembed-
75% dingvectorssuchthatthefrozenLLMisgroundedonthe
observations,andalsopropagateinformationtotheLLM 50%
aboutthecapabilitiesofanembodiment. Trainingsuchen-
codingscanbeunderstoodasaformofinput-conditioned 25%
soft-prompting(Tsimpoukellietal.,2021),inrelationtonor-
0%
malsoftprompts(Lesteretal.,2021). Inexperimentswith TAMP Data Only Lang. Table Data Only SayCan Data Only Full Mixture
PaLM-E (All robots + WebLI,
φ ,wealsofreezetheslotrepresentation,i.e.weonly Training VQA, COCO, etc.)
OSRT Data
updatethesmallprojectorψwhichservesastheinterface
betweenOSRTandtheLLM.
Co-trainingacrosstasks. Inourexperiments,weinvesti-
gate the effects of co-training our models on a variety of
diversedata. The“fullmixture”,seeApp.A,consistspri-
marilyofadiversesetofinternet-scalevision-and-language
data,fromavarietyoftasks. Thesamplingfrequenciesare
setsuchthatonly8.9%ofthefullmixtureisembodieddata,
andthereareseveraltasksforeachembodiment.
6.Experiments
Ourexperimentsconsiderdiverserobotic(mobile)manip-
ulationtasksacrossthreedifferentrobotembodiments,in
simulationandwithtwodifferentrealrobots. Wereferto
https://palm-e.github.ioforvideosshowingthe
capabilities of PaLM-E on those tasks. Although not the
focus of our work, we evaluate PaLM-E also on general
vision-language tasks such as visual-question-answering
(VQA),imagecaptioning,andestablishedlanguagemodel-
ingtasks.
Wesplitourexperimentalinvestigationintotwobroadcate-
gories. First,wecomparethedifferentinputrepresentations
fromSec.4withrespecttoperformance,generalization,and
data-efficiency. Thesecondthreadofexperimentsfocuses
ononearchitecture,themainPaLM-Eversion,consisting
ofapre-trainedViTandPaLMlanguagemodelthattakes
in raw images as the continuous inputs. Here we show
thatasinglemodel,trainedonamixtureofmanydatasets,
across diverse tasks, and across robot embodiments, can
simultaneously achieve high performance on all of those
tasks. Crucially,weinvestigatewhetherco-trainingonthese
datasets enables transfer (Fig. 3): despite different tasks
andembodiments,theperformanceontheindividualtasks
increases by training on the mixture of tasks. We study
theinfluenceonperformance,generalization,anddataef-
ficiency with respect to co-training strategies and model
parametersize. Finally, weconsideriffreezingtheLLM
andjusttrainingtheViTthatinjectsvisionintotheLLMis
aviablepath.
Asbaselines,weconsiderthestate-of-theartvisuallanguage
modelPaLI(Chenetal.,2022),whichhasnotbeentrained
onembodimentrobotdata,aswellastheSayCanalgorithm
(Ahnetal.,2022),suppliedwithoracleaffordances.
ycaruccA
ro
etaR
sseccuS
TAMP Success (Table 1)
Language-Table Success (Table 2)
SayCan Affordances (Table 4)
Different models for different robots, One model for all robots
trained from scratch with ViT + PaLM pre-training
Figure3: OverviewoftransferlearningdemonstratedbyPaLM-
E:acrossthreedifferentroboticsdomains,usingPaLMandViT
pretrainingtogetherwiththefullmixtureofroboticsandgeneral
visual-languagedataprovidesasignificantperformanceincrease
comparedtoonlytrainingontherespectivein-domaindata.See
Tab.1,Fig.4,Tab.2,Tab.4foradditionaldataineachdomain.
6.1.RobotEnvironments/Tasks
Ourthreerobotenvironments(Fig.1)includeaTaskand
Motion Planning (TAMP) domain where a robot has to
manipulate(graspandstack)objects,atable-toppushing
environment,andamobilemanipulationdomain. Ineach
domain, PaLM-E is trained on expert data from that do-
main.Inmanycases,thisisasparseamountofdatapertask.
TheTAMPtasksinvolvelargecombinatoricsoverpossible
plans,andmanydecisionsequencesareinfeasible. PaLM-E
has to generate plans that consist of multiple steps, with
complicateddecisionboundaries. Themulti-objecttabletop
pushingenvironmentistakenfromthepubliclyavailable
Language-Table dataset (Lynch et al., 2022) and is chal-
lengingsinceitincludesseveralobjects,largecardinality
oflanguage,andcomplexpushingdynamics. Forboththe
TAMPandLanguage-Tableenvironment,PaLM-Ehasto
reasonabouttheposesoftheobjects. Itisnotsufficientto
knowwhichobjectsareonthetableorknowingtheirrough
relationships,themorefine-graineddetailsaboutthescene
geometryareimportantforsolvingthetasks. Finally,we
consideramobilemanipulationdomainsimilartoSayCan
(Ahnetal.,2022),wherearobothastosolveavarietyof
tasks in a kitchen environment, including finding objects
in drawers, picking them, and bringing them to a human.
ForalldomainsweconsiderbothplanningandVQAtasks
in those environments. For the mobile manipulation and
Language-Tableenvironments,PaLM-Eisintegratedinto
thecontrollooptoexecutetheplansintherealworld,and
hastoadjusttheplaninpresenceofexternaldisturbances
orfailuresofthelow-levelcontrolpolicies.
6.2.TAMPEnvironment
Tab.7(appendix)showsplanningsuccessratesandVQA
performancefortheTAMPenvironment.TheLLMisfrozen
intheseexperiments(forpre-trainedLLM).Fortheresults

--- Page 7 ---
PaLM-E:AnEmbodiedMultimodalLanguageModel
reported in Tab. 7, the input representations are trained
on a dataset containing 96,000 training scenes of solely
the TAMP environment, i.e. no other data is part of the
mixture. For 3-5 objects in the scene, which is the same
number as in the training set, most input representations
performsimilarlywell. However,whenincreasingthe1n00u%m-
ber of objects, it turns out that using a pre-trained LLM
improvesperformanceconsiderably,especiallywithen75t%ity
referrals. Furthermore, we show that a 62B LLM shows
betterout-of-distributiongeneralizationcomparedtothe50%8B
variant,whileanon-pretrainedLLMshowsbasicallynoout- 0%
25%
of-distributiongeneralization. TheSayCanbaseline(Ahn
et al., 2022) utilizes oracle affordance functions and has
difficultiessolvingthisenvironment,sinceaffordancefunc-
tionsonlyconstrainwhatispossiblerightnow,butarenot
informativeenoughfortheLLMtoconstructlong-horizon
plansinTAMPenvironments.
Tab.1showsresultsfor3-5objectswhentrainingon1%
ofthedataset,whichcorrespondstoonly320examplesfor
TAMP Data Only Lang. Table Data Only SayCan Data Only Full Mixture
eachofthetwoplanningtasks. Hereweseethatthereare (All robots + WebLI,
VQA, COCO, etc.) PaLM-E Training Data
significantdifferencesbetweentheinputrepresentations,es-
peciallyfortheplanningtasks. First,pre-trainingtheLLM
isbeneficialinthelowdataregimeforstateinputs. Second,
bothViTvariants(ViT+TL,ViT-4B)donotperformwell
insolvingtheplanningtasksforthislittledata. However,
if we co-train on all other robot environments as well as
generalvision-languagedatasets(ViT-4Bgeneralist),then
the performance of the ViT-4B more than doubles. This
showsasignificanttransfereffectbetweendifferentrobot
embodimentsandtasks. Finally,usingOSRTastheinput
representationleadstothebestperformancehere,demon-
strating the strengths of 3D-aware object representations.
We also observe another instance of transfer here: when
weremovetheTAMPVQAdataandonlytrainonthe640
planningtasksexamples,thereisa(slight)dropinperfor-
mance. The state-of-the art vision-language model PaLI
(Chen et al., 2022) that was not trained on robot data is
notabletosolvethetasks. Weonlyevaluateditonq (ob-
2
jectsleft/right/centeronthetable)andq (verticalobject
3
relations),sincethosemostresembletypicalVQAtasks.
6.3.Language-TableEnvironment
Tab.2reportssuccessratesonlong-horizontasksfromthe
Language-Tableenvironment(Lynchetal.,2022). PaLM-E
isintegratedintoacontrolloopthattakesasinputthelong-
horizontaskandthecurrentimage,andoutputsaninstruc-
tionforthelow-levelpolicy. Weseethatjointtrainingon
internet-scalevisionandlanguageresultsinamoreeffec-
tivemodelforrobotplanning,particularlyinthefew-shot
regimewithonly10demospertask. Scalingthe12Bmodel
tothe84Bmodelleadstoimprovementson2of3tasks. As
withtheTAMPenvironment,neitherSayCannorzero-shot
PaLIareeffective,unabletosolvetheeasiesttasktested.
ycaruccA
ro
etaR
sseccuS
LLM finetune (full mixture) 94.9%
LLM finetune (single robot) 48.6%
without pretraining 42.9%
LLM frozen (full mixture) 74.3%
LLM frozen (single robot) 31.8%
20% 40% 60% 80% 100%
Figure 4: Planning success results in the TAMP environment
(1%data)forPaLM-E-12B,comparingoftheeffectsofPaLM-E
models(i)usingthefulltrainingmixture,(ii)pre-training(ViT
andPaLM),and(iii)freezingorfinetuningthelanguagemodel.
Transferfromfullmixtureisparticularlyeffective.Notethatfull
mixturecontainsonly1%ofthetrainingdata(320exampleseach)
forthetasksevaluatedhere.Shownisthemeanoftasksp ,p .
1 2
Real Robot Results and Few-Shot Generalization. In
Fig.7,a),weseePaLM-Eiscapableofguidingarealrobot
through a multi-stage tabletop manipulation task, while
remainingrobusttoadversarialdisturbances. Giventheob-
servedimageandalong-horizongoal,e.g.“sorttheblocks
bycolorsintocorners”,PaLM-Eoutputslanguagesubgoals
at1HztothepoliciesfromLynchetal.(2022),thatoutput
low-levelrobotactionsat5Hz. Priorwork(Lynchetal.,
2022)insteadinvolvedahumaninthelooptointeractively
guidesubgoalsandcorrections. InFig.5,b)weseePaLM-
Eiscapableofone-shotandzero-shotlearning. Here,we
finetunedPaLM-Eon100differentlonghorizontaskswith
asingletrainingexampleeach,e.g.“putalltheblocksin
the center”, “remove the blue blocks from the line”. We
additionallyseethatPaLM-Ecangeneralizezero-shotto
tasksinvolvingnovelobjectpairs(Fig.7,c)andtotasksin-
volvingobjectsthatwereunseenineithertheoriginalrobot
datasetorthefinetuningdatasets,e.g.atoyturtle(Fig.5,d).
6.4.MobileManipulationEnvironment
WedemonstratetheperformanceofPaLM-Eonchallenging
anddiversemobilemanipulationtasks. Welargelyfollow
thesetupinAhnetal.(2022),wheretherobotneedstoplan
asequenceofnavigationandmanipulationactionsbasedon
aninstructionbyahuman. Forexample,giventheinstruc-
tion “I spilled my drink, can you bring me something to
cleanitup?”,therobotneedstoplanasequencecontaining
“1. Find a sponge, 2. Pick up the sponge, 3. Bring it to
theuser,4. Putdownthesponge.”Inspiredbythesetasks,
wedevelop3usecasestotesttheembodiedreasoningabil-
ities of PaLM-E: affordance prediction, failure detection,
andlong-horizonplanning. Thelow-levelpoliciesarefrom
RT-1(Brohanetal.,2022),atransformermodelthattakes
RGBimageandnaturallanguageinstruction,andoutputs
end-effectorcontrolcommands.

--- Page 8 ---
PaLM-E:AnEmbodiedMultimodalLanguageModel
Figure5: AsinglePaLM-Emodeldirectsthelow-levelpoliciesoftworealrobots.Shownisalong-horizonmobilemanipulationtaskin
akitchen,andone-shot/zero-shotgeneralizationwithatabletopmanipulationrobot.
Object- LLM EmbodiedVQA Planning etal.,2022c). Themulti-modalpromptisGiven <img>.
centric pre-train q 1 q 2 q 3 q 4 p 1 p 2 Q: Was <skill> successful?. Tab. 4 shows that
SayCan(oracleafford.)(Ahnetal.,2022) (cid:51) - - - - 38.733.3 PaLM-E outperforms PaLI (zero-shot), as well as a fine-
PaLI(zero-shot)(Chenetal.,2022) (cid:51) - 0.0 0.0 - - -
PaLM-E(ours)w/inputenc: tuned version of CLIP on this dataset. PaLM-E also out-
State (cid:51)(GT) (cid:55) 99.4 89.8 90.3 88.345.046.1 performsthealgorithmproposedinXiaoetal.(2022)that
State (cid:51)(GT) (cid:51) 100.096.3 95.1 93.155.949.7
ViT+TL (cid:51)(GT) (cid:51) 34.7 54.6 74.6 91.624.014.7 leveragestwoCLIPmodelstrainedwithhindsightrelabeled
ViT-4Bsinglerobot (cid:55) (cid:51) - 45.9 78.4 92.230.632.9
data. Thismethodhasaccesstomoreinformationthanour
ViT-4Bfullmixture (cid:55) (cid:51) - 70.7 93.4 92.174.174.6
OSRT(noVQA) (cid:51) (cid:51) - - - - 71.975.1 method,andwasspecificallydesignedtojustsolvefailure
OSRT (cid:51) (cid:51) 99.7 98.2100.093.782.576.2
detectiononthisdataset.
Table1:ComparisonofdifferentinputrepresentationsonTAMP
environment(intermsofsuccessrates),wheredatafromTAMP Realrobotresults: Long-horizonplanning. Finally,we
constitutesonly1%(i.e., 320samplesforp , p each)oftotal use PaLM-E to perform embodied planning end-to-end
1 2
trainingdatasize. PaLM-EoutperformsbothPaLIandSayCan for mobile manipulation tasks. The prompt structure for
onembodiedVQAandplanningtasks. Cross-domaintransfer
thistaskisHuman: <instruction> Robot: <step
isobserved,sincethePaLM-EwithViT-4Btrainedonourfull
history>. I see <img>. PaLM-Eistrainedtogener-
datamixtureimprovesplanningperformance.OSRT,despiteusing
nolarge-scaledata,providesthemosteffectiveinputencodings atethenextstepoftheplan,conditionedonthehistoryof
forlearning.(GT)meansground-truthobject-centricinformation takenstepsandthecurrentimageobservationofthescene.
provided.Inallexperiments,theLLMisfrozen.Thenon-object After each step is decoded, we map them to a low-level
centricViT-4Bvariantutilizescolortoreferenceobjects,henceq
1 policyasdefinedinAhnetal.(2022). Thisprocessisdone
cannotbeevaluatedhere.TheLLMisfrozenintheseexperiments
inanautoregressivemanner,untilPaLM-Eoutputs“termi-
(exceptforthecasewhereitisnotpre-trained).Sec.B.1describes
thetasksq -q ,p ,q . nate”.Wetrainthemodelbyusingtherunsfrom (Ahnetal.,
1 4 1 2
2022), which contains 2912 sequences. We qualitatively
evaluatedthemodelinarealkitchenandfoundthemodel
Affordanceprediction. WeinvestigatePaLM-E’sperfor-
cancarryoutlong-horizonmobilemanipulationtasks,even
manceataffordanceprediction,i.e.whetheraskillofthe
underadversarialdisturbances(Fig.5).
low-levelpolicycanbeexecutedinthecurrentenvironment.
ThiscanbeformulatedastheVQAproblemGiven <img>. 6.5.PerformanceonGeneralVisual-LanguageTasks
Q: Is it possible to <skill> here?. PaLM-E
Althoughitisnotthefocusofourwork,wereportinTab.5
outperforms PaLI (zero-shot), as well as thresholding on
results on general vision-language tasks, including OK-
valuefunctionstrainedwithQT-OPT(Tab.4).
VQA(Marinoetal.,2019),VQAv2(Goyaletal.,2017)and
Failuredetection. Forarobottodoclosed-loopplanning, COCOcaptioning(Chenetal.,2015). Asingle,generalist
itisalsoimportanttodetectfailures,asisshownin (Huang

--- Page 9 ---
PaLM-E:AnEmbodiedMultimodalLanguageModel
Zero-shotBaselines Task1 Task2 Task3 Task1.Q:Thereisablockthatisclosestto
SayCan(oracleafford.)(Ahnetal.,2022) 0.0 - - {i.e.,toprightcorner}.Pushthatblockto
PaLI(Chenetal.,2022) 0.0 - - theotherblockofthesamecolor.
trained from LLM+ViT LLM Task #Demos Task2.Q:Howtosorttheblocksbycolors
PaLM-E- on scratch pretrain frozen finetune 10 20 40 10 20 40 10 20 80 intocorners?
12B Singlerobot (cid:51) (cid:55) n/a (cid:51) 20.0 30.0 50.0 2.5 6.3 2.5 11.3 16.9 28.3
12B Fullmixture (cid:55) (cid:51) (cid:51) (cid:55) - - 20.0 - - 36.3 - - 29.4 Task3.Q:Howtopushalltheblocksthat
12B Fullmixture (cid:55) (cid:51) (cid:55) (cid:55) - - 80.0 - - 57.5 - - 50.0 areonthe{left/right}sidetogether,
12B Fullmixture (cid:55) (cid:51) (cid:55) (cid:51) 70.0 80.0 80.0 31.3 58.8 58.8 57.5 54.4 56.3 withoutbringingoveranyoftheblocks
84B Fullmixture (cid:55) (cid:51) (cid:55) (cid:55) - - 90.0 - - 53.8 - - 64.4 thatareonthe{right/left}side?
Table2:ResultsonplanningtasksinthesimulatedenvironmentfromLynchetal.(2022). Table3:TaskpromptsforTab.2.
Baselines Failuredet. Affordance PaLM PaLM-E % drop (relative)
PaLI(Zero-shot)(Chenetal.,2022) 0.73 0.62
60
CLIP-FT(Xiaoetal.,2022) 0.65 -
CLIP-FT-hindsight(Xiaoetal.,2022) 0.89 - 3.9%
QT-OPT(Kalashnikovetal.,2018) - 0.63
PaLM-E-12B from LLM+ViT LLM
trainedon scratch pretrain frozen
40
Singlerobot (cid:51) (cid:55) n/a 0.54 0.46
NLG 61.6%
Singlerobot (cid:55) (cid:51) (cid:51) 0.91 0.78 Tasks
Fullmixture (cid:55) (cid:51) (cid:51) 0.91 0.87 (avg)
Fullmixture (cid:55) (cid:51) (cid:55) 0.77 0.91 87.3%
20
Table4:Mobilemanipulationenvironment:failuredetectionand
affordanceprediction(F1score).
VQAv2 OK-VQA COCO 0
8B 12B 62B 84B 540B 562B
Model test-dev test-std val Karpathytest
Generalist(onemodel)
Figure 6: Results on general language tasks (NLG = natural
PaLM-E-12B 76.2 - 55.5 135.0
languagegeneration):increasingscaleleadstolesscatastrophic
PaLM-E-562B 80.0 - 66.1 138.7
Task-specificfinetunedmodels forgettingbetweenacorrespondingPaLM-Emodelanditsinher-
Flamingo(Alayracetal.,2022) 82.0 82.1 57.8† 138.1 itedPaLMmodel.SeefullsuiteoftasksandresultsinTab.8.
PaLI(Chenetal.,2022) 84.3 84.3 64.5 149.1
PaLM-E-12B 77.7 77.9 60.1 136.0
PaLM-E-66B - - 62.9 -
E-12B)model87.3%ofitsNLGperformance(relative)has
PaLM-E-84B 80.5 - 63.3 138.0
Generalist(onemodel),withfrozenLLM degraded during multimodal training, merely 3.9% have
(Tsimpoukellietal.,2021) 48.4 - - - beendegradedforthelargestmodel(PaLM-E-562B).
PaLM-E-12Bfrozen 70.3 - 51.5 128.0
Table5: Resultsongeneralvisual-languagetasks. Forthegen- 7.SummaryofExperiments&Discussion
eralistmodels,theyarethesamecheckpointacrossthedifferent
Generalist vs specialist models – transfer. As summa-
evaluations, while task-specific finetuned models use different-
finetunedmodelsforthedifferenttasks. COCOusesKarpathy rizedinFig.3,wehaveshownseveralinstancesoftransfer
splits.†is32-shotonOK-VQA(notfinetuned). in this work, meaning that PaLM-E trained on different
tasks and datasets at the same time leads to significantly
increasedperformancerelativetomodelstrainedseparately
PaLM-E-562Bmodelachievesthehighestreportednumber
on the different tasks alone. In Fig. 4, co-training on the
on OK-VQA, including outperforming models finetuned
“fullmixture”achievesmorethandoubletheperformance.
specificallyonOK-VQA.Comparedto(Tsimpoukellietal.,
InTab.9,weseesignificantimprovementsinperformanceif
2021),PaLM-EachievesthehighestperformanceonVQA
weaddLLM/ViTpre-training,andtrainingonthefullmix-
v2withafrozenLLMtothebestofourknowledge. This
tureinsteadofthemobilemanipulationdataalone. Forthe
establishesthatPaLM-Eisacompetitivevisual-language
Language-TableexperimentinTab.2,weobserveanalogous
generalist, in addition to being an embodied reasoner on
behaviour.
robotictasks.
Dataefficiency. Comparedtoavailablemassivelanguage
6.6.PerformanceonGeneralLanguageTasks
or vision-language datasets, robotics data is significantly
Tab.8reportstheaveragedperformanceofPaLM-Eon21 lessabundant. Asdiscussedinthelastparagraph,ourmodel
generallanguagebenchmarksforNaturalLanguageUnder- exhibitstransfer,whichaidsPaLM-Etosolveroboticstasks
standing(NLU)andNaturalLanguageGeneration(NLG) fromveryfewtrainingexamplesintheroboticsdomain,e.g.
tasks. Thenotabletrendisthatwithincreasingmodelscale, between10and80forLanguageTableor320forTAMP.
thereisconsiderablylesscatastrophicforgettingoflanguage TheOSRTresultsshowanotherinstanceofdata-efficiency
capabilities.AsseeninFig.6,whileforthesmallest(PaLM- by using a geometric input representation. A promising

--- Page 10 ---
PaLM-E:AnEmbodiedMultimodalLanguageModel
opportunityforfutureworkistocombinethiswithamethod References
benefittingfromlarge-scalevisualdata.
Ahn,M.,Brohan,A.,Brown,N.,Chebotar,Y.,Cortes,O.,
Retaining language capabilities. We have shown two David,B.,Finn,C.,Gopalakrishnan,K.,Hausman,K.,
pathstoretainthelanguagecapabilitiesofthemodelduring Herzog, A., et al. Do as i can, not as i say: Ground-
multimodaltraining. Asoneoption,freezingtheLLMand ing language in robotic affordances. arXiv preprint
onlytrainingtheinputencodersisaviablepathforbuilding arXiv:2204.01691,2022.
embodiedlanguagemodels,althoughthisapproachocca-
Alayrac, J.-B., Donahue, J., Luc, P., Miech, A., Barr, I.,
sionallystruggledforroboticstasks(Tab.2). Asanalter-
Hasson,Y.,Lenc,K.,Mensch,A.,Millican,K.,Reynolds,
nativeroute,whenthewholemodelistrainedend-to-end,
M.,etal.Flamingo:avisuallanguagemodelforfew-shot
themodelretainssignificantlymoreofitsoriginallanguage
learning. arXivpreprintarXiv:2204.14198,2022.
performancewithincreasingmodelscale(Fig.6).
Bommasani, R., Hudson, D. A., Adeli, E., Altman, R.,
8.Conclusion
Arora,S.,vonArx,S.,Bernstein,M.S.,Bohg,J.,Bosse-
Weproposedtobuildanembodiedlanguagemodelbyin- lut,A.,Brunskill,E.,etal. Ontheopportunitiesandrisks
jectingmulti-modalinformationsuchasimagesintotheem- offoundationmodels. arXivpreprintarXiv:2108.07258,
beddingspaceofapre-trainedLLM.Experimentsshowed 2021.
that off-the-shelf state-of-the-art vision-language models
Brohan,A.,Brown,N.,Carbajal,J.,Chebotar,Y.,Dabis,J.,
trainedongeneralVQAandcaptioningtasksarenotsuffi-
Finn,C.,Gopalakrishnan,K.,Hausman,K.,Herzog,A.,
cientforembodiedreasoningtasks,aswellaslimitationsof
Hsu,J.,etal. Rt-1: Roboticstransformerforreal-world
arecentproposalforgroundinglanguagemodelsthrough
controlatscale. arXivpreprintarXiv:2212.06817,2022.
affordances. Toovercometheselimitations,weproposed
PaLM-E, a single model that is able to control different Brown,T.,Mann,B.,Ryder,N.,Subbiah,M.,Kaplan,J.D.,
robotsinsimulationandintherealworld,whileatthesame Dhariwal, P., Neelakantan, A., Shyam, P., Sastry, G.,
time being quantitatively competent at general VQA and Askell,A.,etal. Languagemodelsarefew-shotlearners.
captioningtasks. Inparticularthenovelarchitecturalideaof Advancesinneuralinformationprocessingsystems,33:
ingestingneuralscenerepresentations(i.e.,OSRT)intothe 1877–1901,2020.
modelisparticularlyeffective,evenwithoutlarge-scaledata.
Changpinyo, S., Kukliansky, D., Szpektor, I., Chen, X.,
PaLM-Eistrainedonamixtureofdiversetasksacrossmul-
Ding,N.,andSoricut,R. Allyoumayneedforvqaare
tiplerobotembodimentsaswellasgeneralvision-language
imagecaptions,2022. URLhttps://arxiv.org/
tasks. Importantly,wehavedemonstratedthatthisdiverse
abs/2205.01883.
trainingleadstoseveralavenuesoftransferfromthevision-
languagedomainsintoembodieddecisionmaking,enabling Chen,M.,Tworek,J.,Jun,H.,Yuan,Q.,Pinto,H.P.d.O.,
robotplanningtaskstobeachieveddataefficiently. While Kaplan,J.,Edwards,H.,Burda,Y.,Joseph,N.,Brockman,
ourresultsindicatethatfrozenlanguagemodelsareaviable G., etal. Evaluatinglargelanguagemodelstrainedon
pathtowardsgeneral-purposeembodiedmultimodalmodels code. arXivpreprintarXiv:2107.03374,2021a.
that fully retain their language capabilities, we have also
surfacedanalternativeroutewithunfrozenmodels: scaling Chen, T., Saxena, S., Li, L., Fleet, D. J., and Hinton, G.
upthelanguagemodelsizeleadstosignificantlylesscatas- Pix2seq: A language modeling framework for object
trophicforgettingwhilebecominganembodiedagent. Our detection. arXivpreprintarXiv:2109.10852,2021b.
largestmodel,PaLM-E-562B,showcasesemergentcapabil-
Chen,X.,Fang,H.,Lin,T.,Vedantam,R.,Gupta,S.,Dolla´r,
ities like multimodal chain of thought reasoning, and the
P.,andZitnick,C.L. MicrosoftCOCOcaptions: Data
abilitytoreasonovermultipleimages,despitebeingtrained
collectionandevaluationserver. CoRR,abs/1504.00325,
ononlysingle-imageprompts.
2015.
Chen, X., Wang, X., Changpinyo, S., Piergiovanni, A.,
Acknowledgements
Padlewski, P., Salz, D., Goodman, S., Grycner, A.,
Theauthorswouldliketothank,fortheiradvice,helpand Mustafa, B., Beyer, L., et al. Pali: A jointly-scaled
support: XiChen,EtiennePot,SebastianGoodman,Maria multilingual language-image model. arXiv preprint
Attarian,TedXiao,KeerthanaGopalakrishnan,KehangHan, arXiv:2209.06794,2022.
HenrykMichalewski,NeilHoulsby,BasilMustafa,Justin
Chowdhery,A.,Narang,S.,Devlin,J.,Bosma,M.,Mishra,
Gilmer,YonghuiWu,EricaMoreira,VictorGomes,Tom
G., Roberts, A., Barham, P., Chung, H.W., Sutton, C.,
Duerig,HenningMeyer,andKendraByrne.
Gehrmann,S.,etal. Palm: Scalinglanguagemodeling
withpathways. arXivpreprintarXiv:2204.02311,2022.

--- Page 11 ---
PaLM-E:AnEmbodiedMultimodalLanguageModel
Dehghani, M., Djolonga, J., Mustafa, B., Padlewski, P., Huang,W.,Abbeel,P.,Pathak,D.,andMordatch,I. Lan-
Heek,J.,Gilmer,J.,Steiner,A.,Caron,M.,Geirhos,R., guagemodelsaszero-shotplanners: Extractingaction-
Alabdulmohsin,I.,etal. Scalingvisiontransformersto able knowledge for embodied agents. arXiv preprint
22billionparameters. arXivpreprintarXiv:2302.05442, arXiv:2201.07207,2022b.
2023.
Huang,W.,Xia,F.,Xiao,T.,Chan,H.,Liang,J.,Florence,
Devlin,J.,Chang,M.-W.,Lee,K.,andToutanova,K. Bert: P.,Zeng,A.,Tompson,J.,Mordatch,I.,Chebotar,Y.,etal.
Pre-training of deep bidirectional transformers for lan- Innermonologue: Embodiedreasoningthroughplanning
guageunderstanding. arXivpreprintarXiv:1810.04805, withlanguagemodels. arXivpreprintarXiv:2207.05608,
2018. 2022c.
Dosovitskiy, A., Beyer, L., Kolesnikov, A., Weissenborn, Jang, E., Irpan, A., Khansari, M., Kappler, D., Ebert, F.,
D.,Zhai,X.,Unterthiner,T.,Dehghani,M.,Minderer,M., Lynch, C., Levine, S., and Finn, C. Bc-z: Zero-shot
Heigold,G.,Gelly,S.,etal. Animageisworth16x16 task generalization with robotic imitation learning. In
words:Transformersforimagerecognitionatscale.arXiv Conference on Robot Learning, pp. 991–1002. PMLR,
preprintarXiv:2010.11929,2020. 2022.
Driess, D., Ha, J.-S., and Toussaint, M. Deep visual rea-
Jiang,Y.,Gupta,A.,Zhang,Z.,Wang,G.,Dou,Y.,Chen,Y.,
soning: Learningtopredictactionsequencesfortaskand
Fei-Fei,L.,Anandkumar,A.,Zhu,Y.,andFan,L. Vima:
motionplanningfromaninitialsceneimage. InProc.of
General robot manipulation with multimodal prompts.
Robotics: ScienceandSystems(R:SS),2020.
arXivpreprintarXiv:2210.03094,2022.
Gan, Z., Li, L., Li, C., Wang, L., Liu, Z., Gao, J., et al.
Kalashnikov,D.,Irpan,A.,Pastor,P.,Ibarz,J.,Herzog,A.,
Vision-language pre-training: Basics, recent advances,
Jang,E.,Quillen,D.,Holly,E.,Kalakrishnan,M.,Van-
andfuturetrends. FoundationsandTrends®inComputer
houcke,V.,etal. Scalabledeepreinforcementlearning
GraphicsandVision,14(3–4):163–352,2022.
forvision-basedroboticmanipulation. InConferenceon
RobotLearning,pp.651–673.PMLR,2018.
Glaese,A.,McAleese,N.,Trebacz,M.,Aslanides,J.,Firoiu,
V.,Ewalds,T.,Rauh,M.,Weidinger,L.,Chadwick,M.,
Kojima,T.,Gu,S.S.,Reid,M.,Matsuo,Y.,andIwasawa,
Thacker, P., et al. Improving alignment of dialogue
Y. Largelanguagemodelsarezero-shotreasoners. arXiv
agents via targeted human judgements. arXiv preprint
preprintarXiv:2205.11916,2022.
arXiv:2209.14375,2022.
Lester,B.,Al-Rfou,R.,andConstant,N.Thepowerofscale
Goyal, Y., Khot, T., Summers-Stay, D., Batra, D., and
for parameter-efficient prompt tuning. arXiv preprint
Parikh, D. Making the V in VQA matter: Elevating
arXiv:2104.08691,2021.
theroleofimageunderstandinginVisualQuestionAn-
swering. InConferenceonComputerVisionandPattern
Lewkowycz, A., Andreassen, A., Dohan, D., Dyer, E.,
Recognition(CVPR),2017.
Michalewski, H., Ramasesh, V., Slone, A., Anil, C.,
Schlag,I.,Gutman-Solo,T.,etal. Solvingquantitative
Guhur, P.-L., Chen, S., Garcia, R., Tapaswi, M., Laptev,
reasoningproblemswithlanguagemodels.arXivpreprint
I., and Schmid, C. Instruction-driven history-aware
arXiv:2206.14858,2022.
policies for robotic manipulations. arXiv preprint
arXiv:2209.04899,2022.
Li, L. H., Yatskar, M., Yin, D., Hsieh, C.-J., and Chang,
Hao,Y.,Song,H.,Dong,L.,Huang,S.,Chi,Z.,Wang,W., K.-W. Visualbert: Asimpleandperformantbaselinefor
Ma,S.,andWei,F.Languagemodelsaregeneral-purpose visionandlanguage. arXivpreprintarXiv:1908.03557,
interfaces. arXivpreprintarXiv:2206.06336,2022. 2019.
Hu, X., Gan, Z., Wang, J., Yang, Z., Liu, Z., Lu, Y., and Li,M.,Lv,T.,Chen,J.,Cui,L.,Lu,Y.,Florencio,D.,Zhang,
Wang, L. Scaling up vision-language pre-training for C.,Li,Z.,andWei,F. Trocr: Transformer-basedoptical
imagecaptioning. InProceedingsoftheIEEE/CVFCon- character recognition with pre-trained models. arXiv
ferenceonComputerVisionandPatternRecognition,pp. preprintarXiv:2109.10282,2021.
17980–17989,2022.
Li,S.,Puig,X.,Du,Y.,Wang,C.,Akyurek,E.,Torralba,
Huang, C., Mees, O., Zeng, A., and Burgard, W. Vi- A.,Andreas,J.,andMordatch,I. Pre-trainedlanguage
suallanguagemapsforrobotnavigation. arXivpreprint modelsforinteractivedecision-making. arXivpreprint
arXiv:2210.05714,2022a. arXiv:2202.01771,2022.

--- Page 12 ---
PaLM-E:AnEmbodiedMultimodalLanguageModel
Liang,J.,Huang,W.,Xia,F.,Xu,P.,Hausman,K.,Ichter, Ryoo,M.S.,Piergiovanni,A.,Arnab,A.,Dehghani,M.,and
B.,Florence,P.,andZeng,A.Codeaspolicies:Language Angelova,A.Tokenlearner:Whatcan8learnedtokensdo
model programs for embodied control. arXiv preprint forimagesandvideos? arXivpreprintarXiv:2106.11297,
arXiv:2209.07753,2022. 2021.
Locatello,F.,Weissenborn,D.,Unterthiner,T.,Mahendran, Sajjadi, M. S. M., Duckworth, D., Mahendran, A., van
A.,Heigold,G.,Uszkoreit,J.,Dosovitskiy,A.,andKipf, Steenkiste, S., Pavetic´, F., Lucˇic´, M., Guibas, L. J.,
T. Object-centriclearningwithslotattention. Advances Greff, K., and Kipf, T. Object Scene Representa-
in Neural Information Processing Systems, 33:11525– tion Transformer. NeurIPS, 2022a. URL https:
11538,2020. //osrt-paper.github.io/.
Lu, J., Batra, D., Parikh, D., and Lee, S. Vilbert: Pre- Sajjadi,M.S.M.,Meyer,H.,Pot,E.,Bergmann,U.,Greff,
trainingtask-agnosticvisiolinguisticrepresentationsfor K., Radwan, N., Vora, S., Lucˇic´, M., Duckworth, D.,
vision-and-languagetasks. Advancesinneuralinforma- Dosovitskiy,A.,etal. Scenerepresentationtransformer:
tionprocessingsystems,32,2019. Geometry-free novel view synthesis through set-latent
scenerepresentations. InProceedingsoftheIEEE/CVF
Lu,K.,Grover,A.,Abbeel,P.,andMordatch,I. Pretrained
ConferenceonComputerVisionandPatternRecognition,
transformers as universal computation engines. arXiv
pp.6229–6238,2022b.
preprintarXiv:2103.05247,1,2021.
Shah, D., Osinski, B., Ichter, B., and Levine, S. Lm-
Lynch, C. and Sermanet, P. Language conditioned imi-
nav: Robotic navigation with large pre-trained mod-
tation learning over unstructured data. arXiv preprint
els of language, vision, and action. arXiv preprint
arXiv:2005.07648,2020.
arXiv:2207.04429,2022.
Lynch, C., Wahid, A., Tompson, J., Ding, T., Betker, J.,
Sharma,P.,Ding,N.,Goodman,S.,andSoricut,R. Con-
Baruch,R.,Armstrong,T.,andFlorence,P. Interactive
ceptualcaptions: Acleaned,hypernymed,imagealt-text
language: Talkingtorobotsinrealtime. arXivpreprint
datasetforautomaticimagecaptioning. InProceedings
arXiv:2210.06407,2022.
ofACL,2018.
Marino,K.,Rastegari,M.,Farhadi,A.,andMottaghi,R.Ok-
Sharma, P., Torralba, A., and Andreas, J. Skill induc-
vqa: Avisualquestionansweringbenchmarkrequiring
tionandplanningwithlatentlanguage. arXivpreprint
externalknowledge. InConferenceonComputerVision
arXiv:2110.01517,2021.
andPatternRecognition(CVPR),2019.
Shridhar,M.,Manuelli,L.,andFox,D. Cliport: Whatand
Nair, S., Mitchell, E., Chen, K., Savarese, S., Finn, C.,
wherepathwaysforroboticmanipulation. InConference
etal. Learninglanguage-conditionedrobotbehaviorfrom
onRobotLearning,pp.894–906.PMLR,2022a.
offlinedataandcrowd-sourcedannotation. InConference
onRobotLearning,pp.1303–1315.PMLR,2022. Shridhar,M.,Manuelli,L.,andFox,D. Perceiver-actor: A
multi-tasktransformerforroboticmanipulation. arXiv
Nottingham,K.,Ammanabrolu,P.,Suhr,A.,Choi,Y.,Ha-
preprintarXiv:2209.05451,2022b.
jishirzi,H.,Singh,S.,andFox,R. Doembodiedagents
dreamofpixelatedsheep?: Embodieddecisionmaking Silva,A.,Moorman,N.,Silva,W.,Zaidi,Z.,Gopalan,N.,
usinglanguageguidedworldmodelling. arXivpreprint andGombolay,M.Lancon-learn:Learningwithlanguage
arXiv:2301.12050,2023. toenablegeneralizationinmulti-taskmanipulation.IEEE
RoboticsandAutomationLetters,7(2):1635–1642,2021.
Piergiovanni,A.,Kuo,W.,andAngelova,A. Pre-training
image-languagetransformersforopen-vocabularytasks, Singh, I., Blukis, V., Mousavian, A., Goyal, A., Xu, D.,
2022. URL https://arxiv.org/abs/2209. Tremblay,J.,Fox,D.,Thomason,J.,andGarg,A. Prog-
04372. Prompt: Generatingsituatedrobottaskplansusinglarge
language models. arXiv preprint arXiv:2209.11302,
Polu,S.,Han,J.M.,Zheng,K.,Baksys,M.,Babuschkin,I.,
2022.
andSutskever,I. Formalmathematicsstatementcurricu-
lumlearning. arXivpreprintarXiv:2202.01344,2022. Tellex,S.,Gopalan,N.,Kress-Gazit,H.,andMatuszek,C.
Robots that use language. Annual Review of Control,
Reed, S., Zolna, K., Parisotto, E., Colmenarejo, S. G.,
Robotics,andAutonomousSystems,3:25–55,2020.
Novikov, A., Barth-Maron, G., Gimenez, M., Sulsky,
Y.,Kay,J.,Springenberg,J.T.,etal. Ageneralistagent. Thoppilan, R., De Freitas, D., Hall, J., Shazeer, N., Kul-
arXivpreprintarXiv:2205.06175,2022. shreshtha,A.,Cheng,H.-T.,Jin,A.,Bos,T.,Baker,L.,

--- Page 13 ---
PaLM-E:AnEmbodiedMultimodalLanguageModel
Du,Y.,etal. Lamda: Languagemodelsfordialogappli-
cations. arXivpreprintarXiv:2201.08239,2022.
Tsimpoukelli, M., Menick, J. L., Cabi, S., Eslami, S.,
Vinyals, O., and Hill, F. Multimodal few-shot learn-
ing with frozen language models. Advances in Neural
InformationProcessingSystems,34:200–212,2021.
Wang,Z.,Cai,S.,Liu,A.,Ma,X.,andLiang,Y. Describe,
explain,planandselect: Interactiveplanningwithlarge
languagemodelsenablesopen-worldmulti-taskagents.
arXivpreprintarXiv:2302.01560,2023.
Wei, J., Wang, X., Schuurmans, D., Bosma, M., Chi, E.,
Le,Q.,andZhou,D. Chainofthoughtpromptingelic-
itsreasoninginlargelanguagemodels. arXivpreprint
arXiv:2201.11903,2022.
Xiao, T., Chan, H., Sermanet, P., Wahid, A., Brohan, A.,
Hausman, K., Levine, S., and Tompson, J. Robotic
skillacquisitionviainstructionaugmentationwithvision-
language models. arXiv preprint arXiv:2211.11736,
2022.
Zellers,R.,Holtzman,A.,Peters,M.,Mottaghi,R.,Kem-
bhavi, A., Farhadi, A., and Choi, Y. Piglet: Language
grounding through neuro-symbolic interaction in a 3d
world. arXivpreprintarXiv:2106.00188,2021a.
Zellers, R., Lu, X., Hessel, J., Yu, Y., Park, J.S., Cao, J.,
Farhadi, A., and Choi, Y. Merlot: Multimodal neural
scriptknowledgemodels. AdvancesinNeuralInforma-
tionProcessingSystems,34:23634–23651,2021b.
Zeng,A.,Wong,A.,Welker,S.,Choromanski,K.,Tombari,
F., Purohit, A., Ryoo, M., Sindhwani, V., Lee, J., Van-
houcke, V., et al. Socratic models: Composing zero-
shotmultimodalreasoningwithlanguage. arXivpreprint
arXiv:2204.00598,2022.
Zhang, Y. and Chai, J. Hierarchical task learning from
languageinstructionswithunifiedtransformersandself-
monitoring. arXivpreprintarXiv:2106.03427,2021.
Zhou,L.,Palangi,H.,Zhang,L.,Hu,H.,Corso,J.,andGao,
J. Unifiedvision-languagepre-trainingforimagecaption-
ingandvqa. InProceedingsoftheAAAIConferenceon
ArtificialIntelligence,2020.

--- Page 14 ---
PaLM-E:AnEmbodiedMultimodalLanguageModel
… …
… …
… …
PaLM-E
Figure7: PaLM-Einteractivelyguidesarealrobotthroughlong-horizonmanipulationtasksonLanguage-Table,whileremainingrobust
toadversarialdisturbances.WefindevidencethatPaLM-Eiscapableofone-shotandzeroshotgeneralization.
A.DataMixture
Tab.6showsthedatasetandsamplingfrequencyforthe“fullmixture”asreferredtointheexperiments. Themajorityofthe
datadistributionisgeneralvision-languagetasks,withlessthan10%robotdata.
B.EnvironmentDetails
B.1.TaskandMotionPlanning(TAMP)
ThetrainingscenesfortheTAMPenvironmentcontain3-5cube-shapedobjectsofdifferentsizes,colorsandsampledinitial
poses. Fig.8showanexampletestscenethatcontains6objects.
Intheglobalversion,weconsiderthefollowingthreeVQAtasks:

--- Page 15 ---
PaLM-E:AnEmbodiedMultimodalLanguageModel
Datasetinfullmixture Samplingfrequency %
Webli(Chenetal.,2022) 100 52.4
VQ2A(Changpinyoetal.,2022) 25 13.1
VQG(Changpinyoetal.,2022) 10 5.2
CC3M(Sharmaetal.,2018) 25 13.1
ObjectAware(Piergiovannietal.,2022) 10 5.2
OKVQA(Marinoetal.,2019) 1 0.5
VQAv2(Goyaletal.,2017) 1 0.5
COCO(Chenetal.,2015) 1 0.5
Wikipediatext 1 0.5
(robot)MobileManipulator,real 6 3.1
(robot)LanguageTable(Lynchetal.,2022),simandreal 8 4.2
(robot)TAMP,sim 3 1.6
Table6:Datasetsamplingfrequencyandratioforthe“fullmixture”referredtoinexperiments.
Figure8:TwoTAMPenvironmenttestexamples.Leftwith6objects(trainingdatacontains3-5objects),rightwith4objects.
• q : object-table relation. Example prompt: Given <img>. Q: Is the red object left, right,
2
or center of the table?. Target: A: The red object is in the center of the table.
• q : object-objectrelations. Exampleprompt: Given <img>. Q: Is the yellow object below the
3
blue object?. Target: A: No, the yellow object is not below the blue object.
• q : plan feasibility. Example prompt: Given <img>. Q: Is it possible to first grasp the
4
blue object, then place it on the yellow object, and then grasp the yellow
object?. Target: A: No, this is not possible.
aswellasthetwoplanningtasks
• p : grasping. Example prompt: Given <img>. Q: How to grasp the green object?. Tar-
1
get: A: First grasp the orange object and place it on the table, then grasp the
green object.
• p : stacking. Example prompt: Given <img>. Q: How to stack the white object on top
2
of the red object?. Target: A: First grasp the green object and place it on the
table, then grasp the white object and place it on the red object.
Fortheobject-centricversionwithentityreferrals,allpromptscontaintheprefix<prefix>=Obj 1 is <obj >. ...
1
Obj j is <obj >.,andtheVQAtaskq isaboutthecolorofanobject. Theothertasks(exceptwiththedifferent
j 1
prefix,andentityreferrals),remainthesame.
WeutilizetheplannerfromDriessetal.(2020)togeneratethedatasetfortheplanningtasks. Thelow-levelpoliciesarealso
obtainedwiththemethodofDriessetal.(2020).

--- Page 16 ---
PaLM-E:AnEmbodiedMultimodalLanguageModel
φ LLMpre-trained q q q q p p
1 2 3 4 1 2
SayCan(w/oracleaffordances) (cid:51) - - - - 38.7 33.3
state (cid:55) 100.0 99.3 98.5 99.8 97.2 95.5
state (cid:51)(unfrozen) 100.0 98.8 100.0 97.6 97.7 95.3
state (cid:51) 100.0 98.4 99.7 98.5 97.6 96.0
3-5 state(w/oentityreferrals) (cid:51) 100.0 98.8 97.5 98.1 94.6 90.3
objects ViT+TL(obj.centric) (cid:51) 99.6 98.7 98.4 96.8 9.2 94.5
ViT+TL(global) (cid:51) - 60.7 90.8 94.3 70.7 69.2
ViT-4B(global) (cid:51) - 98.2 99.4 99.0 96.0 93.4
ViT-4Bgeneralist (cid:51) - 97.1 100.0 98.9 97.5 95.2
OSRT (cid:51) 99.6 99.1 100.0 98.8 98.1 95.7
state (cid:55) 20.4 39.2 71.4 85.2 56.5 34.3
6
state (cid:51) 100.0 98.5 94.0 89.3 95.3 81.4
objects
state(w/oentityreferrals) (cid:51) 77.7 83.7 93.6 91.0 81.2 57.1
state (cid:55) 18.4 27.1 38.1 87.5 24.6 6.7
8
state (cid:51) 100.0 98.3 95.3 89.8 91.3 89.3
objects
state(w/oentityreferrals) (cid:51) 60.0 67.1 94.1 81.2 49.3 49.3
state(8BLLM) (cid:55) - 0 0 72.0 0 0
6objects+
state(8BLLM) (cid:51) - 49.3 89.8 68.5 28.2 15.7
OODtasks
state(62BLLM) (cid:51) - 48.7 92.5 88.1 40.0 30.0
Table7: SuccessratesonTAMPenvironmentfordifferentinputrepresentations. 3-5objectsinthescenecorrespondtothetraining
distribution.OODtasksmeansout-of-distributiontaskswheretheobjectsarereferencedbycolor,althoughinthetrainigdatatheyhave
beenreferencedbytheirspecialtokensobj intheobject-centriccase.TheSayCanbaseline(Ahnetal.,2022)utilizesoracle,one-step
j
affordancefunctions.
B.2.InteractiveLanguageTable
WeusetheLanguage-Tablereal-worldtabletopsetupandsimulatedenvironmentfromInteractiveLanguage(Lynchetal.,
2022).
Datacollection. Foreachtask,giventhelonghorizoninstruction,wepromptalabelertoenterashorthorizoncommand
every4seconds. WepasstheshorthorizoninstructionstoanInteractiveLanguagepolicytrainedusingthesameprocedure
asinLynchetal.(2022). Thepolicyexecutes40steps(10Hzfor4seconds)beforerequiringanothercommandfromthe
labeler. Thisisrepeateduntilthelabelerdeterminesthelonghorizoninstructioniscompleteandissuesa’done’instruction.
Thedatacollectionprocedurefortherealworldexperimentsarethesameasinsimulation.
TrainandEvaluation. Totrainthefinetunedversionsofthesemodels,wetrainapretrainedPaLM-Emodelfor9,000
additionalsteps, inordertosupportadatacomplexitysweepwithouttrainingseveralseparatemodelsfromscratchon
slightly different versions of the full mixture. For Tasks 2 and 3 in simulation, we implement an automated reward to
measurethesuccessrate,andweevaluatePaLM-Ebyrunning80rolloutsforeachtask. Giventhecurrentimageandhigh
leveltask,PaLM-Eissuesatextinstructionwhichatrainedlow-levelpolicyexecutesfor4secondsbeforePaLM-Eissuesa
newtextinstruction. ForTask1,weuseatest-setandreportvalidationaccuracy. Thisisbecausethetaskonlyrequiresone
steptosolve,despitebeingacomplicatedvisualandlinguisticprocessingtaskandcannotbesolvedbythelow-levelpolicy
fromthepromptalone.

--- Page 17 ---
PaLM-E:AnEmbodiedMultimodalLanguageModel
C.NaturalLanguageGenerationandUnderstandingResults
PaLM-8B PaLM-E-12B PaLM-62B PaLM-E-84B PaLM-540B PaLM-E-562B Category
1-shotevals (unfrozen) (unfrozen) (unfrozen)
TriviaQA(wiki)(EM) 48.5 10.1 72.7 31.8 81.4 74.6 NLG
NaturalQuestions(EM) 10.6 1.6 23.1 7.6 29.3 27.2 NLG
WebQuestions(EM) 12.6 3.4 19.8 7.9 22.6 21.8 NLG
Lambada 57.8 1.4 75.5 26.1 81.8 83.3 NLG
HellaSwag 68.2 48.4 79.7 75.3 83.6 83.5 NLU
StoryCloze 78.7 68.7 83.8 83.9 86.1 86.3 NLU
Winograd 82.4 71.8 85.3 86.4 87.5 89.0 NLU
Winogrande 68.3 55.3 76.8 72.5 83.7 83.0 NLU
RACE-M 57.7 43.2 64.1 57.4 69.3 70.3 NLU
RACE-H 41.6 33.2 48.7 42.3 52.1 52.8 NLU
PIQA 76.1 68.1 80.9 78.2 83.9 84.9 NLU
ARC-e 71.3 53.4 78.9 71.4 85.0 86.3 NLU
ARC-c 42.3 30.9 51.8 46.7 60.1 62.6 NLU
OpenBookQA 47.4 41.4 51.2 51.6 53.6 55.8 NLU
BoolQ 64.7 61.6 83.1 81.6 88.7 89.4 NLU
Copa 82.0 77.0 93.0 91.0 91.0 93.0 NLU
RTE 57.8 54.9 71.5 59.6 78.7 75.1 NLU
Wic 50.6 50.0 48.6 50.2 63.2 64.1 NLU
WSC 81.4 68.4 84.9 75.8 86.3 85.6 NLU
ReCoRD 87.8 71.2 91.0 78.5 92.8 92.5 NLU
CB 41.1 37.5 55.4 73.2 83.9 80.3 NLU
AvgNLU 64.7 55.0 72.3 69.2 78.2 78.5
AvgNLG 32.4 4.1 47.8 18.4 53.8 51.7
NLUdelta(%,relative) -15.0% -4.3% +0.4%
NLGdelta(%,relative) -87.3% -61.6% -3.8%
Table8:FulllanguageevaluationtaskresultsonbothNLUandNLGtasks,forboththeoriginalPaLMmodelsandforassociatedPaLM-E
(unfrozen)models.ThePaLM-EmodelswithafrozenLLMhavethesameperformanceastheircorrespondingunderlyingPaLMmodels.

--- Page 18 ---
PaLM-E:AnEmbodiedMultimodalLanguageModel
D.AdditionalDataforAffordanceandSuccessDetection
Model Precision Recall F1-score
PaLI(Zero-shot)(Chenetal.,2022) 0.59 0.98 0.73
CLIP-FT(Xiaoetal.,2022) 0.50 0.95 0.65
CLIP-FT-hindsight(Xiaoetal.,2022) 1.0 0.80 0.89
PaLM-E-12B from LLM+ViT LLM
trainedon scratch pretrain frozen
Singlerobot (cid:51) (cid:55) n/a 0.52 0.55 0.54
Singlerobot (cid:55) (cid:51) (cid:51) 0.91 0.92 0.91
Fullmixture (cid:55) (cid:51) (cid:51) 0.89 0.93 0.91
Fullmixture (cid:55) (cid:51) (cid:55) 0.66 0.91 0.77
Table9:Mobilemanipulationenvironment:failuredetection,showingindividualprecisionandrecallscores.
Model Precision Recall F1-score
PaLI(Zero-shot)(Chenetal.,2022) 0.57 0.69 0.62
QT-OPT(Kalashnikovetal.,2018) 0.60 0.67 0.63
PaLM-E-12B from LLM+ViT LLM
trainedon scratch pretrain frozen
Singlerobot (cid:51) (cid:55) n/a 0.67 0.35 0.46
Singlerobot (cid:55) (cid:51) (cid:51) 0.90 0.69 0.78
Fullmixture (cid:55) (cid:51) (cid:51) 0.95 0.80 0.87
Fullmixture (cid:55) (cid:51) (cid:55) 0.92 0.88 0.91
Table10:Mobilemanipulationenvironment:affordanceprediction,showingindividualprecisionandrecallscores.
E.ImageAttribution
The image of the New York Knicks and Boston Celtics in Figure 2 is under the terms CC-by-2.0 (https://
creativecommons.org/licenses/by/2.0/),andwaspostedtoFlickrbykowarskiathttps://www.flickr.
com/photos/27728232@N00/8666371367. The egocentric video images are from https://youtu.be/
-UXKmqBPk1w,asin(Zengetal.,2022),viapermissionfromcreatorCodyWanner.