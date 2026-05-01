--- Page 1 ---
RoboAgent:
Generalization and Efficiency in Robot Manipulation
via Semantic Augmentations and Action Chunking
HomangaBharadhwaj∗,1,2 JayVakil∗,2 MohitSharma∗,1
AbhinavGupta1 ShubhamTulsiani1 VikashKumar1,2
1CarnegieMellonUniversity,2FAIR-MetaAI
https://robopen.github.io/ 
Pick Lid
Cap Lid
Slide-Close Drawer
Flap-Close Oven
Pick Towel
Wipe Counter
nehctiK
naelC
Pick Tea
Place Tea
Pick Lid
Cap Lid
aeT
ekaM
Slide-Open Drawer
Pick Butter
Uncap Lid
Place Butter
Place Lid
Slide-Close Drawer
perP
gnikaB
Slide-Open Drawer
Pick Bowl
Slide-In Bowl
Slide-Close Drawer
lwoB
wotS
Flap-Open Oven
Slide-out Bowl
Place Bowl
Flap-Close Oven
puoS
evreS
Flap-Open Oven
Pick Bowl
Slide-In Bowl
Flap-Close Oven
puoS
taeH
MT-ACT
Skills ⇒ Slide-Close Slide-Open Pick Place Flap-Open Flap-Close Cap Uncap Slide-in Slide-out Wipe Press
Figure1: AglimpseofthediversemanipulationcapabilitiesofRoboAgent–asingleagentcapableof12ma-
nipulationskillsacross38tasksencompassing6activities.Forvideos,visit:robopen.github.io/ 
Abstract: The grand aim of having a single robot that can manipulate arbitrary
objects in diverse settings is at odds with the paucity of robotics datasets. Ac-
quiringandgrowingsuchdatasetsisstrenuousduetomanualefforts,operational
costs,andsafetychallenges. Apathtowardsuchanuniversalagentwouldrequire
a structured framework capable of wide generalization but trained within a rea-
sonable data budget. In this paper, we develop an efficient system (RoboAgent)
for training universal agents capable of multi-task manipulation skills using (a)
semanticaugmentationsthatcanrapidlymultiplyexistingdatasetsand(b)action
representationsthatcanextractperformantpolicieswithsmallyetdiversemulti-
modaldatasetswithoutoverfitting. Inaddition,reliabletaskconditioningandan
expressive policy architecture enable our agent to exhibit a diverse repertoire of
skillsinnovelsituationsspecifiedusinglanguagecommands. Usingmerely7500
∗authorscontributedequally
3202
peS
5
]OR.sc[
1v81910.9032:viXra

--- Page 2 ---
demonstrations,weareabletotrainasingleagentcapableof12uniqueskills,and
demonstrate its generalization over 38 tasks spread across common daily activi-
tiesindiversekitchenscenes.Onaverage,RoboAgent outperformspriormethods
by over 40% in unseen situations while being more sample efficient and being
amenabletocapabilityimprovementsandextensionsthroughfine-tuning.
1 Introduction
Trainingarobotmanipulator withmultipleskillsrequiresexposuretodiverseexperiences andthe
abilitytoacquireskillsfromadiversedatacorpus. Tocollectsuchamulti-skilldatacorpusinthe
realworldrequiressubstantialeffortandsuffersfromhighoperationalcostsandsafetychallenges.
Given the expense, efficiency in robot learning paradigms is necessary for real-world training and
deployment. Whiletherearerecenteffortsinscalingreal-worldroboticdatasetsdespitethesechal-
lenges[1,2,3],efficiencyseemstobeoverlookedintheattemptstoscale[4,5,6,7].
With the acknowledgment that robot learning will generally benefit as the scale of the robotics
datasetgrows,thefocusofourworkisoninvestigatinggeneralizationindevelopingcapableagents
underagivendatabudget. Werestrictourselvestoadatasetwith7,500robotmanipulationtrajec-
tories(anorderofmagnitudelessthanrelatedworks[5])containingadiversecollectionofmanip-
ulationskillsacrossdifferenttasks. Asarobotunderdeploymentinrealenvironmentslikehomes,
hospitals, etc., will always find itself in unseen scenarios, we set out to develop the most capable
agentwithanemphasisonitsabilitytogeneralizetonovelsituationswithinthisdatabudget.
Atfirstsight,widegeneralizationwithadatabudgetseemslikewishfulthinking-whileit’spossi-
ble to provide large representation capabilities to the agent’s policy, scaling without data diversity
will likely lead to overfitting and no generalization. Our insight is twofold: (1) We ensure suffi-
cientcoverageofdifferentskillsindifferentscenariosinadataset(of7500trajectories)wecollect
throughteleoperation. Thecollecteddatasetisdiversifiedoffline,atnoextrahuman/robotcost,via
semanticaugmentations [8,9,10]toaidgeneralizationinnovelsituations. (2)Wetrainalanguage-
conditionedmanipulationpolicywithMT-ACT–multi-taskaction-chunkingtransformerscapable
ofhandlingthemulti-modaldatadistribution. Thearchitectureleveragesthefactthatrobotmove-
mentsaretemporallycorrelated,bypredictingactionchunks[11]insteadofper-stepactions,leading
tosmootherbehaviorsandmitigationofcovariateshiftcommonlyobservedinthelowdataimitation
learningregime.
Overall,weemphasizethatthedataefficiencylessonswepresentaregeneralandwillhelpinachiev-
ing generalizable agents independent of the available data budget. Building on these insights, we
makethefollowingcontributions:
• WepresentanefficientmethodMT-ACTdesignedtorecovergeneralistagentsonadatabudget.
MT-ACTleveragesdatamultiplicationviasemanticaugmentationsandactionrepresentationsto
driveefficiencygainsinlow-datasettings.
• MT-ACT’sarchitecturecaneffectivelyingestmulti-modaltrajectorydatatorecoverRoboAgent –
a single policy that can perform a diverse set of tasks through language instructions. Through
extensivereal-worldexperiments,weshowRoboAgent iscapableofexhibiting12manipulation
skills.
• We perform extensive generalization studies to demonstrate that MT-ACT is 40 % more perfor-
mantthanalternatives,exhibitsmuchsuperiorgeneralizationtodiversenovelscenarios,andis
amenabletoimprovementsandextensionsduringdeploymentthroughfine-tuning.
• Wemeticulouslyrecordedallthedatacollectedduringthecourseoftheprojectwhichweareopen-
sourcing as part of RoboSet - one of the largest open-source robotics dataset on commodity
hardware. Itcontainshigh-qualityhumanteleOptrajectoriesspanningabalanceddistributionof
12skillsacross38tasksindiversekitchenscenes.
2

--- Page 3 ---
Offline Training Online Inference
Semantic Augmentation via Foundation Models
Encoder
(text) User Input
FiLM
MMpMo pMlo pav lo pav loecav l ecaev ec F e ec F e t rF e ot u rFot u r o i ttur t o ihtus tiht s te iht stf e h srf e b orf e b orfom b orom baooma ormt a dr ht a dh rt e dr hte dh e e CNN
Action Chunking
MT-ACT
Small Offline Dataset
Temporal Aggregation
Policy Architecture
Figure 2: Twostageframework: [Left]Semanticaugmentationstagediversifiestherobotdataofflineus-
ing inpainting augmentations at no extra human/robot cost. [Right] Policy learning stage trains language-
conditionedpolicyusingMT-ACT–multi-taskaction-chunkingtransformers–whichleveragesefficientaction
representationsforingestingmulti-modalmulti-taskdataintoasinglemulti-skillmulti-taskpolicy.
2 RelatedWork
Frameworks for Scaling Robot Learning. Given the cost of supervision in robot learning, self-
supervisedlearning[12,13,14]methodsleveraginglargeunlabeleddatasetshavebeenadominant
paradigm in efforts towards building general-purpose agents. Large-scale simulations [15, 16, 17,
18]havealsobeenleveragedwiththehopeoflearningageneralmulti-taskpolicyfordiversetasks
[19, 20, 21, 22, 23,24] first and then transferring it to thereal world via sim2real[25, 26, 27, 28].
However,manyexistingmulti-taskRLworksfocusonnarrowdomainsinsimulation[22,29],and
those in the real-world show limited generalization and task diversity [30, 9]. While other works
[19, 20, 31] focus on multi-task settings in diverse scenarios, they restrict to evaluating trained
policies mostly in simulation. By contrast, our work focuses on a large, diverse set of real-world
manipulationtasks. Recently,manyworkshaveusedimitationlearningwithlarge-scalereal-world
robottele-operationdatasetsofhighquality[2,3,32,1,33,34]. Whileearlyworkscollectlimited
real-world data [3, 33], more recent approaches [1, 5, 7] collect much larger datasets. In fact, [5]
gathers, possibly, the largest dataset (≈ 130K demonstrations) outside bin and place settings and
showsimpressivegeneralizationwithskillslearnedusingthisdata.Ourworkissimilarinspirit,i.e.,
wefocusonreal-worldmanipulationtasksandaimtolearnamulti-taskpolicyusinglimited real-
worlddemonstrations. However,unlike[1],weavoidtoyenvironmentsetupsandfocusonrealistic
real-worldkitchensetupswithclutterandmultiplefeasibletasksinascene.Additionally,ouragents
exhibitamuchgreaterdiversityofskillsthan[5,7,28]whilebeingtrainedonlyon7.5ktrajectories,
asopposedto135kin[5]. Importantly,wecollectourdatawithcommodityhardware(seeFigure6)
andaremakingitreadilyavailabletoroboticresearchersworldwide.
Alternate Data Sources in Robotics. Recent successes of large-scale self-supervised approaches
within both language and vision communities have showcased the advantage of large-scale data.
Manyrecentworksproposeusingpre-trainedvisualrepresentationstrainedprimarilyonnon-robot
datasets [35, 36], for learning control policies [37, 38, 26, 39, 40]. Most of these works focus on
single-tasksettings[37,38,41,42],orinsimulatedrobotenvironments[26,39]. Giventheinher-
entlylargecostofcollectingreal-worldroboticsdatasets,manyworkshavefocusedonusingalter-
natedatasourcessuchaslanguage[43,44,45,46],humanvideos[47,48,49,50,51,52,53,54],
andgenerativeaugmentations[55,56,9,8,10]. Ourworkismostsimilartothelattersetofworks,
someofwhichusediffusionmodelstogenerateaugmentationsfordatacollectedintherealworld.
However,unlikesomepriorworks[9,8]ourapproachisfullyautomatic. Wedonotneedsegmen-
tationmasks[9]orobjectmeshes[8]forgeneratingaugmentationdata. Overall,ourworkismost
similar to [10] which adapts a pre-trained open-world object detection model [57] for generating
3

--- Page 4 ---
Table 1: Open-source real-world manipulation dataset landscape: RoboSet(ours) https://
robopen.github.io/roboset/ is one of the largest open-source robotics datasets. It contains
high-qualitydemonstration,includinghumantele-operation,trajectoriesspanningabalanceddistri-
butionof12skillsacross38tasksindiversekitchenscenes.
Trajectories Tasks Skills Scenes Source
RoboSet(MT-ACT) 7,500 38 12 10 TeleOp
RoboSet(kitchen) 30,050 38 12 10 TeleOp
RoboSet(bin) 70,000 10 4 1 Heuristics
RoboSet(full) 98,050 48 12 11 TeleOp+Heuristics
BridgeData[1] 33,200 72 8 10 TeleOp
BC-Z[6] 25,000 100 9 N/A TeleOp
RoboTurk[3] 2,100 N/A 3 1 TeleOp
AmazonPick-Place[60] 100,000 N/A 1 1 Heuristics
RoboNet[2] 162,000 N/A 2 7 Heuristics
BAIRPushing[61] N/A N/A 1 1 Heuristics
segmentationsthatareusedwithtext-guideddiffusionmodelstogenerateaugmentations. However,
our approach does not require any further fine-tuning of a separate module for open-vocabulary
segmentationandlanguagegrounding. Moreimportantly, wefurtherinvestigatescalinglawswith
respect to semantic data augmentations to demonstrate the favorable impact of augmentations in
aidingtest-timegeneralizationtounseenscenarios.
3 MT-ACT: Multi-TaskActionChunkingTransformer
To learn generalizable manipulation policies, it is essential for robots to be exposed to rich and
diverse experiences, encompassing a wide range of skills and contextual variations. However, op-
erationalcostsandreal-worldchallengesincollectingsuchextensivedatasetsposeapracticallimit
on their overall size. Our goal is to address these limitations by developing a paradigm that can
learneffectivemulti-taskagentsunderalimiteddatabudget. Ourapproachconsistsoftwostages
(Figure2):
SemanticAugmentation–thefirststagemultipliesthepre-collecteddatasetbycreatingadiverse
collection of semantic augmentations over the existing robot’s experiences. These semantic aug-
mentations recreate a particular robot demonstration into several demonstrations, each with a dif-
ferentsemanticcontext(objects,textures,backgrounds,etc),atnoextrarobotorhumancost. Such
datadiversificationincorporatesreal-worldsemanticpriorsintothemulti-taskmanipulationagents
preparingthemtoaccountforout-of-distributionscenariostheymightencounterduringdeployment.
Policy Learning – the second stage learns robust skills from limited skill data, adapting design
choices from previously limited single-task settings to the context of large-scale generalization in
multi-taskmulti-scenemanipulationtaskswithdiverseskills. WedevelopMT-ACT–alanguage-
conditioned novel policy architecture to train robust agents capable of recovering multiple skills
from multi-modal datasets. To model the diverse multi-modal multi-task augmented datasets, we
employ a Conditional Variational Autoencoder (CVAE) [58] to identify action distribution modes.
Thisenablesustofitahigh-capacityTransformer[59]conditionedontheCVAEencodings,effec-
tivelycapturingthevariationsanddependenciesintheaugmenteddataset.Ourpolicyalsoleverages
the fact that robot movements are temporally correlated. Predicting action chunks [11] instead of
per-stepactions,leadstosmootherbehaviorsandmitigationofcovarianceshiftcommonlyobserved
inthelowdataimitationlearningregime.Next,weoutlinetheindividualcomponentsofourmethod
indetail.
3.1 Dataset(RoboSet)
Trainingageneralagentcapableofrobustlyexhibitingadiverserepertoireofskillsinnovelscenes
andtasksneedsexposuretoexperiencesmatchingthisdiversity. Toalignwithourgoalofbuilding
4

--- Page 5 ---
a data-efficient robot learning paradigm, we restrict ourselves to a frozen pre-collected small but
diversedataset–RoboSet(MT-ACT). Inordertocapturebehavioraldiversity,weensuresufficient
coverageoverdifferentcoreskills, whereeachskillifdefinedasatemporallycorrelatedsequence
ofactionsthatleadtoplausiblechangeinanobject’spose. Exampleskillsincludeclosing/opening
articulatedobjects,sliding,wiping.Eachskillisinstantiatedacrossasetofobjects.Werefertosuch
(skill,object)combinationsasatask. Ourtasksareinstantiatedindifferentkitchenscenes,visually
illustratedinAppendixA. Insteadofarandomcollectionoftasks,westructuregroupsoftasksas
belongingtobepartofahouseholdactivity, suchthattheycanbeexecutedinsequencetoobtain
ameaningfuloutcome,suchascleaningakitchen. Furtherdetailsonthedifferentskills,tasksand
activitiesinRoboSetareprovidedinAppendixA.1.
30
1900
25
20 1350
15
750 750
10 500 500 500
5 250 250 250 250 250
0
Pick Place Flap-Close Slide-Close Cap
Flap-
Open
Slide-
Open Press Slide-in
Slide-
Out Uncap Wipe
egatnecreP
tesataD
Figure 3: RoboSet(MT-ACT) contains a diverse set of 12 non-trivial manipulation skills (beyond pick-
ing/pushing, including articulated object manipulation and object re-orientation) expressed across 38 tasks
acrossmultiplescenes. Inthefigure,wemarktheskilldistributionofourdatasetintermsof%oftrajectories
withacertainskill.Thenumberontoprepresentsthenumberoftrajectoriescorrespondingtotheskillusedto
trainRoboAgent.
RoboSet(MT-ACT) – the dataset we used for this project consists of 7,500 trajectories (Table 1)1
collectedusinghumanteleoperation. Thedatasetinvolves12skillsexpressedacrossmultipletasks
and scenes. Figure 3 shows the distribution of skills over our dataset. While the commonly used
pick-placeskillscover40%ofthedataset,wealsoincludecontact-richskillssuchas(Wipe,Cap)as
wellasskillsinvolvingarticulatedobjects(Flap-Open,Flap-Close). Wecollecttheoveralldataset
across four different physical setups. Each setup is instantiated with various everyday objects to
createakitchenscene. Wefrequentlyvaryeachsetupwithdifferentvariationsofobjects,thereby
exposingeachskilltomultipletargetobjectsandsceneinstantiations. Weprovideaglimpseofthe
overallsetupandasubsetofobjectsusedinFigure6,anddatacompositiondetailsinsection4.
In Table 1, we compare our dataset with existing open-source robot manipulation datasets. Com-
paredtoprioropen-sourcereal-worlddatasets,RoboSetpresentsagreaternumberanddiversityof
skillsandscenevariations. RoboSetisoneofthelargestpublicallyreleaseddatasetwithcommod-
ityrobotscollectedinthereal-worldsetup. Finally, despiteourdatadiversity, RoboSet(MT-ACT)
used for training our agents is still much smaller in size in comparison to other recent papers that
use proprietary robotic hardware, e.g. RT1 which has 135K trajectories [5], or those that rely on
simulation[28].
3.2 DataAugmentation
Generally useful robot manipulation systems will need to be able to deal with out-of-distribution
scenarios(e.g. differenthomesandoffices). Sinceanydatasetofapracticalsizewillhavealimited
diversityofobjectsandscenes(duetophysicalaccessandoperationalconstraints)comparedtowhat
agentswillencounterduringdeployment.Toenabletest-timegeneralizationtotheunseenscenarios,
wedevelopafullyautomaticofflineprocesstomultiplythedataset.
1Note that the entire RoboSet is much larger and much more diverse. RoboAgent is trained on
RoboSet(MT-ACT)–asubsetconsistingof7500trajectories
5

--- Page 6 ---
(cid:11)(cid:68)(cid:12) (cid:36)(cid:88)(cid:74)(cid:80)(cid:72)(cid:81)(cid:87)(cid:76)(cid:81)(cid:74)(cid:3)(cid:37)(cid:68)(cid:70)(cid:78)(cid:74)(cid:85)(cid:82)(cid:88)(cid:81)(cid:71) (cid:3)(cid:3)(cid:3)(cid:3)(cid:3)(cid:3)(cid:3)(cid:3)(cid:3)(cid:3)(cid:11)(cid:69)(cid:12)(cid:3)(cid:3)(cid:3)(cid:3)(cid:3)(cid:36)(cid:88)(cid:74)(cid:80)(cid:72)(cid:81)(cid:87)(cid:76)(cid:81)(cid:74)(cid:3)(cid:44)(cid:81)(cid:87)(cid:72)(cid:85)(cid:68)(cid:70)(cid:87)(cid:76)(cid:82)(cid:81)(cid:3)(cid:50)(cid:69)(cid:77)(cid:72)(cid:70)(cid:87)
Figure 4: Illustration of the data augmentations that we develop to rapidly multiply limited robot datasets
withdiversesemanticscenevariations. In(a)weshowthescenearoundtherobotandtheinteractionobject
changing.In(b),weshowtheinteractionobjectitselfchangingwhilepreservingtherestofthescene.
Given an initial dataset of robot behaviors, we multiply the dataset by creating multiple semantic
variationsofthedatasetwhilepreservingtherobotbehaviorwithineachtrajectory. Thesesemantic
variations are created by applying augmentations per frame within the trajectory. Augmentations
are created by inpainting a part of the image frame introducing new objects and scene variations.
The inpainting locations are specified by a mask and are informed by a text prompt. As opposed
to [9, 8, 10] needing manual masks, object templates, etc., our approach is fully automatic. We
use the SegmentAnything model [62] to automatically detect semantic boundaries in the scene to
create augmentation masks. We apply augmentations separately to the object under manipulation
andtherestoftheenvironmentrespectingtheobjectandrobotboundaries. SeesubsectionA.2for
additional details. We emphasize that our approach toward semantic augmentation is fully auto-
maticandoffline. Ittakesadvantageofandisalsowellpoisedtocontinuallybenefitfromrapidly
advancingprogressinsegmentationandin-paintingmodels[62,63]. Akintofieldsofnaturallan-
guage processing and computer vision, by distilling semantic real-world priors present in internet
images/videosintoroboticsdatasets,itprovidesrobotlearningascalablemechanismtobenefitfrom
internet-scaledataatnoextracosttohumans/robots.
3.3 MT-ACTArchitecture
Scaling up dataset diversity as well as network capacity constitutes the two fundamental require-
mentstoimprovegeneralizationinmachinelearningparadigms. Inthefieldofrobotlearning, the
needforgeneralizationremainsatlargeasbothoftheaforementionedgenerationrequirementsare
hard to meet under real-world constraints. Safety and operational costs challenge the availability
ofdiversedatasets,andtheneedforfastreal-timecontrolloopsrestrictstheinferencetimeneeded
toavaillargemodels. Recoveryofageneralizablerobotmanipulationpolicyunderapracticaldata
budgetavailableinroboticsdemandsanefficientpolicyarchitecture.Inscenariosthathavesufficient
coverage within the training data, we want the policy to stay close to nominal behaviors (efficient
imitation). The policy also needs to be effective to new variations (effective generalization) and
contexts(efficienttaskconditioning)thatareunseenduringtraining. Inaddition,wewantthepoli-
ciestoexhibittemporallycorrelatedsmoothbehaviorsaccomplishingtaskswithminimalerrorsand
safetyviolations.
Ourpolicyarchitecture–MT-ACTisdesignedtobeaTransformermodel[59]ofsufficientcapacity
that can handle multi-modal multi-task robot datasets. In order to capture multi-modal data, fol-
lowingpriorworks[11]weincorporateaCVAE[58]thatencodesactionsequencesintolatentstyle
embeddings z. The decoder of the CVAE is the Transformer policy that conditions on the latents
z. Thisformulationofexpressingthepolicyasagenerativemodelhelpsineffectivelyfittingtothe
multi-modalteleopdata,withoutignoringregionsofatrajectorycrucialforprecision,whicharealso
likelytobemorestochastic.Inordertomodelmulti-taskdata,weincorporateapre-trainedlanguage
encoder[65]thatlearnsanembeddingT ofaparticulartaskdescription. Tomitigateissuesofcom-
6

--- Page 7 ---
Figure 5: Policy architecture for MT-ACT . We use a CVAE that learns latent encodings z for action se-
quencestoimplicitlyidentifydifferentmodesinthedata. Atransformertakesasinputalatentcode,language
embeddingofthetask, andimageembeddingsfromfourcameraviews, toautoregressivelyoutputanaction
sequence a for chunk size H. On the right, we shows details for the FiLM layer [64] that we use for
t:t+H
language-conditioning.
pounding error and to achieve smooth temporally correlated robot motions, at each time-step, we
predictactionsH stepsinthefutureandexecutethemthroughtemporal-aggregationofoverlapping
actionspredictedforaparticulartime-step[11]. Toimproveeffectivenesstowardsscenevariations
androbustnesstowardsocclusionsinclutter,weprovidethepolicywithfourdifferentviewsofthe
workspacethroughfourcameras.
Attime-stept,thetransformerencodertakesfourcameraviews,o1:4,thejointposeoftherobotj ,
t t
thestyleembeddingfromtheCVAEz,andthelanguageembeddingT. WeuseaFiLM-basedcon-
ditioning[64,5],inordertoensurethattheimagetokensareabletoreliablyfocusonthelanguage
instruction,suchthatthepolicydoesn’tgetconfusedaboutthetaskwhenmultipletasksarepossible
in a scene. The encoded tokens go to the decoder of the Transformer policy with fixed position
embeddings,whichfinallyoutputsthenextactionchunk(H actions)forthecurrenttime-step. For
execution, weaverageoveralloverlappingactionspredictedforthecurrenttime-step(AsH > 1,
theactionchunksoverlap),andexecutetheresultingaveragedaction.
4 ExperimentalDesign
Throughexperiments,wewanttounderstandthefollowingresearchquestions
• HowdoesMT-ACTperform,quantitativelyandqualitatively,onalargesetofvision-basedrobotic
manipulationtasks? Howdoesitgeneralizetonewtasks,objects,andenvironments?
• Doesdataaugmentationimproverobustnesstonoise/distractors?
• Doesdataaugmentationimprovepolicygeneralization(i.e. sceneswithnewtargetobjects)?
• DoesthepolicyarchitectureofMT-ACTenableefficientlearningwithhighperformance?
• Doesactionchunkinghelpwithtemporallyconsistenttrajectories,achievinghighersuccess?
Toanswertheseresearchquestionsweinstantiateourframeworkintherealworldusingcommodity
hardwareandobjectscommonlyusedineverydaykitchens. Next,weoutlinethesystemanddataset
usedtoinvestigateourquestionsandthendescribethedifferentgeneralizationaxesforevaluation.
Robothardware. Figure6showsourrobotenvironment,calledRoboPenthatconsistsofakitchen
setupwitheverydayobjects,aFrankaEmikaPandaarmwithatwo-fingerRobotiqgripperfittedwith
Festo Adaptive Fingers2, three fixed cameras (top, left, right), and a wrist camera mounted above
the end-effector. The four Realsense D455 camera views provide complementary perspectives of
theworkspace,andweutilizeallofthemforrobustpolicylearning.
2https://robotiq.com/products/2f85-140-adaptive-robot-gripper and https://www.
festo.com/us/en/p/adaptive-gripper-finger-id_DHAS_GF/
7

--- Page 8 ---
Datacollection. Ourrobotmanipulationdatasetfortheexperimentsconsistsof7,500trajectories,
collectedthroughtele-operationbyahumanoperator, overaperiodoftwomonths. Wecollectall
thedataacrossfourdifferentphysicalsetupswithdifferentkitchen-likeenvironmentswithaFranka
Emika [66]. Each setup also sporadically changes its scene by swapping new objects and back-
grounds. Theteleoperationstackisbasedon[67]andusesVR-controllers. Thedatasetcomprises
of diverse manipulation skills like opening/closing drawers, pouring, pushing, dragging, picking,
placing,etc. acrossseveraleverydayobjects. Figure3showsthedistributionofskillsinthedataset.
Additional details regarding the dataset, along with sample trajectories, and a link to the entire
dataset are in the project website  linked with the paper. We are publicly releasing this dataset,
aspartofRoboSet–alargemulti-skillroboticsdatasetdescribedinsubsection3.1. Toourknowl-
ed(cid:42)ge(cid:79),(cid:76)t(cid:80)his(cid:83)is(cid:86)o(cid:72)n(cid:3)e(cid:82)o(cid:73)f(cid:3)t(cid:50)he(cid:69)la(cid:77)r(cid:72)ge(cid:70)st(cid:87)(cid:86)op(cid:3)e(cid:76)n(cid:81)-s(cid:3)o(cid:53)ur(cid:82)ce(cid:69)r(cid:82)ob(cid:54)ot(cid:72)m(cid:87)a(cid:3)n(cid:68)ip(cid:81)ul(cid:71)at(cid:3)io(cid:48)n(cid:55)da(cid:16)ta(cid:36)se(cid:38)ts(cid:55)with the most commonly
used non-proprietary robot hardware (Franka Panda [66]) containing diverse real-world behaviors
beyondpickandplace.
(cid:53)(cid:82)(cid:69)(cid:82)(cid:87)(cid:3)(cid:54)(cid:72)(cid:87)(cid:88)(cid:83) (cid:42)(cid:79)(cid:76)(cid:80)(cid:83)(cid:86)(cid:72)(cid:3)(cid:82)(cid:73)(cid:3)(cid:50)(cid:69)(cid:77)(cid:72)(cid:70)(cid:87)(cid:86)(cid:3)(cid:76)(cid:81)(cid:3)(cid:53)(cid:82)(cid:69)(cid:82)(cid:54)(cid:72)(cid:87)
Figure 6: Azoomed-outviewoftherobotenvironment, showingallfourcamerasinthescene(incolored
squares) that provide complementary views of the scene and a glimpse of the diverse set of objects in the
dataset, used for all our experiments. The objects range from articulated objects like drawers and ovens, to
smallerrigidobjectslikefrenchpress,bowls,anddeformableobjectsliketowels.
Figure7: Visualizationofdifferentgeneralizationaxes,evaluatingeffectivenesswithlightingvariationsand
smallerscenechangessuchasobjectposes(L1),robustnesstosignificantscenevariations(L2),generalization
tounseentasks(L3). Bottom-Left: ResultsforcommonlyusedL1-generalization. Bottom-Right: Multi-Task
(universalpolicy)resultsfordifferentlevelsofgeneralization.See9forL4-generalizationresults.
GeneralizationAxes. Followingpriorwork[5,6,20],wedefineeachtasktoconsistofaparticular
languagecommandlike‘pickacubeofbutterfromthedrawerontheleft’thatdefinesanobjectto
8

--- Page 9 ---
beinteractedwith(butter),askilltobeexecuted(pick),andsomecontext(drawerontheleft). Each
activityconsistsofacollectionof4-5closelytasksthatcanbeexecutedinsequence. Table2lists
thedifferentactivitiesusedinourwork. Werefertothepolicytrainedoveralltheactivitiestobe
theuniversalpolicy, andthosetrainedonlyoveroneactivitytobeanactivitypolicy. Weconsider
evaluations in terms of different levels of generalization, illustrated visually for a scene in Fig. 7:
L1(Effectiveness):Generalizationoftheagenttovariationsinobjectpositionsandorientations,and
in lighting conditions. L2 (Robustness): New background, different distractor object variations,
andunseendistractorobjectsintroducedinthescene. L3(Generalization): Newtasksneverseen
before,includingnewobject-skillcombinations. L4(StrongGeneralization): Newkitchennever
seenbefore(seeFigure9Left).
5 Experiments
Throughdetailedreal-worldrobotmanipulationexperiments,weevaluatetheproposedframework
forsampleefficiency,andgeneralizationoftheagenttodiversescenes.
Baselines. Wecomparemultiplebaselinesthatusevisualpolicylearningforrobotics. SingleTask
Agents: We compare ACT-based policies [11] trained for individual tasks, and evaluated on the
respective tasks. These policies don’t need to generalize across tasks and scene, and represent
an approximate oracle performance per task. Visual Imitation Learning (VIL): We compare with
regular language-conditioned multi-task visual imitation learning. CACTI [9]: This baseline is a
prior framework for multi-task learning that also uses some scene augmentations for generaliza-
tion. RT1 [5]: We re-implement a baseline RT1-like agent. BeT [68]: We modify the Behavior
Transformerarchitecturewithlanguageconditioningandtrainitinamulti-taskmanner.
Next, we present results and analysis from our large-scale real-world experiments that attempt to
understandtheresearchquestionspresentedinsection4.
5.1 Multi-TaskReal-WorldResults
Performance. Figure7(Left-Bottom)comparesourproposedMT-ACTpoliciesagainstcommonly
usedimitationlearningarchitectures. Inthisfigure(Figure7Left-Bottom)weonlyplotresultsfor
L1-generalizationsincethisisthestandardsettingmostotherimitationlearningalgorithmsuse. We
observe that all approaches that only model next-step actions (instead of sub-trajectories) exhibit
weaker performance. Among these approaches, we find that action-clustering-based approaches
(BeT [68]) for multi-task settings, perform significantly worse. We believe this happens because
naiveclusteringinverydiverseactiondistributionsmaynotresultinclustersthatgeneralizeacross
diverse skills. Additionally, since we are operating under a data budget, we observe that RT1-like
approaches that require a lot of data do not perform well in the low data regime. By contrast,
ourMT-ACTpolicywhichusesaction-chunkingandCVAEtomodelmulti-modalsub-trajectories
significantlyoutperformsallbaselines.
GeneralizationandRobustness. Figure7(Bottom-Right)showstheresultsforallmethodsacross
multiplelevelsofgeneralization(L1,L2,andL3). Recallthattheselevelsofgeneralizationinclude
diverse table backgrounds, distractors (L2) and novel skill-object combinations (L3). From Fig-
ure 7 (Bottom-Right) we see that by virtue of semantic augmentations and action representations,
MT-ACTsignificantlyoutperformsallthebaselinesweconsider. Moreinterestingly,weseethatse-
manticaugmentationshavelesseffectforL1-generalization(≈ 30%relative),theyprovideamuch
moresignificantimprovementforbothL2-generalization(≈ 100%relative)andL3-generalization
(≈ 400% relative). Since semantic augmentations affect both scenes (backgrounds and distractor
objects) as well as target objects being manipulated they provide useful support for the policy to
achieveincreasinglevelsofgeneralization.
Additionally, in Figure 8 we also separately report generalization results for each ac-
tivity separately. From Figure 8 we see that each our proposed semantic augmen-
tations positively affect each activity’s performance. Interestingly, we find that for
9

--- Page 10 ---
Figure8:ResultsforMT-ACT,itsablatedvariantwithoutsemanticaugmentations,andbaselines,fordifferent
activities,withL1,L2,L3levelsofgeneralization. Eachactivityconsistsof4-5tasks,andtheresultsaverage
overthetasksinanactivity. Theresultsshowthatsemanticaugmentationssignificantlyimproveperformance
ofMT-ACToverthebaselines. Inaddition,evenwithoutaugmentations,theMT-ACTpolicyachievesmuch
highersuccessratescomparedtothebaselines.
some of the harder activities (Making-Tea, Stowing-Bowl, Heating Soup) the rel-
ative improvement in performance due to semantic augmentations is much larger.
Overall,ourresultsshowthattraditionalvisualimitation
learning(withoutanyaugmentations),i.e.,VILandRT1
trainedonourrelativelysmalldataset,completelyfailfor
L3 and L2, indicating a lack of generalization to unseen
scenarios, due to data paucity. Finally, we also test our
policyonacompletelynewkitchenwithnovelobjects,ar-
rangements, distractors, i.e., L4generalization. Figure9
(Left)visualizesthisnewkitchenenvironment. Weeval-
uateallmethodsinthisnewkitchenfor3tasks. Figure9
(Right) shows the results for each method on this new
environment. Specifically, we obtain an average success
rate of 25% for MT-ACT (and 0 for all the other base-
Figure 9: OnlyMT-ACTpoliciesperform
lines). WeseethatMT-ACTwithoutsemanticaugmenta-
tasks in a completely new kitchen environ-
tionsalsofailscompletelyonthisnewenvironmentthus ment(L4).
indicatingthebenefitsofourapproachforzero-shotadap-
tation.
5.2 Ablation
Weablatethedifferentdesignchoiceswemakeinourproposedarchitecture.
TaskSpecificationusingFiLMconditioning. Forlanguageconditionedmulti-taskpolicy, asde-
scribedinsection3.3,weuseaFiLMbasedconditioning[64]forthelanguageembeddingoftask
descriptions [69]. Here, we compare this design choice with a simple concatenation-based condi-
tioning of the language embeddings with image tokens for the policy. In Fig. 10 (Left) we show
resultsforthisablationstudyaveragedoverallactivities, andweobservea5-10%dropinperfor-
manceoftheversionofMT-ACTwithoutFiLMconditioning.
ChunkSizeforActionRepresentations. HerewetrainvariantsofMT-ACTwithdifferentchunk
sizes10,20,40.InFig.10((Middle-Left),weseethatachunksizeof20performsthebest,witha0-
5%dropinperformancewithchunksize10. Inaddition,largechunksize40performssignificantly
worsewithmorethan20%dropinperformanceindicatingtheinabilityofthepolicytocorrecterrors
asthechunksgrowinsize.
10

--- Page 11 ---
Figure10: Weshowsresultsofthedifferentablationstudiesandanalysisinsection5.2,showingthebenefits
ofFiLMconditioning,theeffectofvaryingchunksizesinthepredictions,thenumberofaugmentationsper
frameformultiplyingthedataset,andthefeasibilityoffine-tuningMT-ACTforimproveddeployment.
Numberofaugmentationsperframe. Weablatethenumberofaugmentationsperframe, tosee
ifmoreaugmentationshelpMT-ACTinlearningamoreperformantpolicy. FromFig.10(Middle-
Right),weseethatthenumberofaugmentationsperframeisstronglycorrelatedwithoverallperfor-
mancegains. Thankstothereal-worldsemanticpriorsinjectedviadataaugmentation,thegainsare
morenotableforL2andL3levelswhereout-of-domaingeneralizationisrequiredfromthepolicy.
Robustnessanalysis. WeperformseveralrobustnessanalysesoftheuniversalMT-ACTagent,by
manually perturbing the scene during evaluation, and also introduce system failures like blocking
the views from one, two, or three cameras. On average, we find that the policy is robust to these
strongactivevariations,andcansolvethespecifiedtaskinabout70%ofthe20evaluationswerun
forthisanalysis. Videosshowingtheseresultsareintheprojectwebsite.
Plasticity. Here, we evaluate the feasibility of adding additional capabilities to the universal
MT-ACT agent, without requiring significant re-training. We take the trained agent (on 38 tasks)
andfine-tuneon(1/10)th oftheoriginaldatacombinedwithdataforanewheld-outtask(placing
toastintoasteroven). Thenewtaskhas50trajectories,multipliedwith4augmentationsperframe,
foratotalof250trajectories.Fig.10(Right)showsthatthefine-tunedagentisabletolearnthisnew
task,withoutsignificantlydeterioratinginperformanceontheprevious6activities.Also,itachieves
slightlybetterL2,L3performancethanasingle-taskpolicytrainedonlyonaugmenteddataofthe
newtask,indicatingefficientdatare-use.
6 DiscussionandLimitations
Wedevelopedaframeworkforsample-efficientandgeneralizablemulti-taskrobotmanipulationin
therealworld. Ourframeworkisbasedonrapidlymultiplyingasmallroboticsdatasetthroughse-
manticsceneaugmentations, andtrainingamulti-tasklanguage-conditionedpolicythatcaningest
the diverse multi-modal data obtained through augmentations. We combine and adapt several de-
sign choices like action chunking and temporal aggregation proposed in the context of single-task
policies, andshowthattheyyieldsignificantboostsinperformanceeveninthemulti-tasksettings
weconsider.
Finally,wereleaseoneofthelargestrobotmanipulationdatasetstodateinvolvingover12skillsin
kitchenenvironmentswhichwehopewillfacilitatefurtherresearchindevelopingrobotmanipula-
tionsystemswithdiversereal-worldgeneralization. Animportantlimitationofourworkisthatall
thetasksconsistofindividualskills,andaninterestingdirectionforfutureworkwouldbetodevelop
approaches for composing skills automatically for solving long-horizon tasks. Another limitation
is that we do not explore the axes of language generalization, and use language embeddings from
pre-trainedencodersasis,withoutanymodifications. Futureworkcouldinvestigatebetterlanguage
conditioningthatismoreflexiblyadaptabletochangesintaskdescriptions.
11

--- Page 12 ---
Acknowledgements
We acknowledge various contributions, large and small, from the entire Embodied AI team at
Meta. The project has also significantly benefitted from brainstorming sessions from – Aravind
Rajeswaran, Chris Paxton, Tony Zhao, Abhishek Gupta, and individual contributions from Giri
Anantharaman, Leonid Shamis, Tingfan Wu, Priyam Parashar, Chandler Meadows, Sahir Gomez,
and Liyiming Ke. We thank Gaoyue Zhou, Raunaq Bhirangi, Sudeep Dasari , Yufei Ye, Mustafa
Mukadam, Shikhar Bahl, Mandi Zhao, Wenxuan Zhou, Jason Ma, and Unnat Jain for helpful dis-
cussionsatdifferentstagesoftheproject.
References
[1] F. Ebert, Y. Yang, K. Schmeckpeper, B. Bucher, G. Georgakis, K. Daniilidis, C. Finn, and
S.Levine. Bridgedata: Boostinggeneralizationofroboticskillswithcross-domaindatasets.
[2] S. Dasari, F. Ebert, S. Tian, S. Nair, B. Bucher, K. Schmeckpeper, S. Singh, S. Levine, and
C.Finn. Robonet: Large-scalemulti-robotlearning. InConferenceonRobotLearning,pages
885–897.PMLR,2020.
[3] A.Mandlekar,Y.Zhu,A.Garg,J.Booher,M.Spero,A.Tung,J.Gao,J.Emmons,A.Gupta,
E.Orbay,etal. Roboturk: Acrowdsourcingplatformforroboticskilllearningthroughimita-
tion. InConferenceonRobotLearning,pages879–893.PMLR,2018.
[4] D.Kalashnikov,J.Varley,Y.Chebotar,B.Swanson,R.Jonschkowski,C.Finn,S.Levine,and
K. Hausman. Mt-opt: Continuous multi-task robotic reinforcement learning at scale. arXiv
preprintarXiv:2104.08212,2021.
[5] A.Brohan,N.Brown,J.Carbajal,Y.Chebotar,J.Dabis,C.Finn,K.Gopalakrishnan,K.Haus-
man,A.Herzog,J.Hsu,etal. Rt-1:Roboticstransformerforreal-worldcontrolatscale. arXiv
preprintarXiv:2212.06817,2022.
[6] E.Jang,A.Irpan,M.Khansari,D.Kappler,F.Ebert,C.Lynch,S.Levine,andC.Finn. Bc-z:
Zero-shottaskgeneralizationwithroboticimitationlearning. InConferenceonRobotLearn-
ing,pages991–1002.PMLR,2022.
[7] D. Kalashnikov, A. Irpan, P. Pastor, J. Ibarz, A. Herzog, E. Jang, D. Quillen, E. Holly,
M.Kalakrishnan,V.Vanhoucke,etal.Qt-opt:Scalabledeepreinforcementlearningforvision-
basedroboticmanipulation. arXivpreprintarXiv:1806.10293,2018.
[8] Z.Chen,S.Kiami,A.Gupta,andV.Kumar. Genaug: Retargetingbehaviorstounseensitua-
tionsviagenerativeaugmentation. arXivpreprintarXiv:2302.06671,2023.
[9] Z. Mandi, H. Bharadhwaj, V. Moens, S. Song, A. Rajeswaran, and V. Kumar. Cacti:
A framework for scalable multi-task multi-scene visual imitation learning. arXiv preprint
arXiv:2212.05711,2022.
[10] T. Yu, T. Xiao, A. Stone, J. Tompson, A. Brohan, S. Wang, J. Singh, C. Tan, J. Peralta,
B.Ichter,etal. Scalingrobotlearningwithsemanticallyimaginedexperience. arXivpreprint
arXiv:2302.11550,2023.
[11] T.Z.Zhao, V.Kumar, S.Levine, andC.Finn. Learningfine-grainedbimanualmanipulation
withlow-costhardware. arXivpreprintarXiv:2304.13705,2023.
[12] L. Pinto and A. Gupta. Learning to push by grasping: Using multiple tasks for effective
learning. In 2017 IEEE international conference on robotics and automation (ICRA), pages
2161–2168.IEEE,2017.
[13] C.Lynch,M.Khansari,T.Xiao,V.Kumar,J.Tompson,S.Levine,andP.Sermanet. Learning
latentplansfromplay. InConferenceonrobotlearning,pages1113–1132.PMLR,2020.
12

--- Page 13 ---
[14] L. Berscheid, T. Ru¨hr, and T. Kro¨ger. Improving data efficiency of self-supervised learning
forroboticgrasping. In2019InternationalConferenceonRoboticsandAutomation(ICRA),
pages2125–2131.IEEE,2019.
[15] T. Yu, D. Quillen, Z. He, R. Julian, K. Hausman, C. Finn, and S. Levine. Meta-world: A
benchmarkandevaluationformulti-taskandmetareinforcementlearning. InConferenceon
robotlearning,pages1094–1100.PMLR,2020.
[16] S.James,Z.Ma,D.R.Arrojo,andA.J.Davison. Rlbench: Therobotlearningbenchmark&
learningenvironment. IEEERoboticsandAutomationLetters,5(2):3019–3026,2020.
[17] M.Mittal,C.Yu,Q.Yu,J.Liu,N.Rudin,D.Hoeller,J.L.Yuan,R.Singh,Y.Guo,H.Mazhar,
etal.Orbit:Aunifiedsimulationframeworkforinteractiverobotlearningenvironments.IEEE
RoboticsandAutomationLetters,2023.
[18] Y. Zhu, J. Wong, A. Mandlekar, R. Mart´ın-Mart´ın, A. Joshi, S. Nasiriany, and Y. Zhu. ro-
bosuite: Amodularsimulationframeworkandbenchmarkforrobotlearning. arXivpreprint
arXiv:2009.12293,2020.
[19] S.Reed,K.Zolna,E.Parisotto,S.G.Colmenarejo,A.Novikov,G.Barth-Maron,M.Gimenez,
Y. Sulsky, J. Kay, J. T. Springenberg, et al. A generalist agent. arXiv preprint
arXiv:2205.06175,2022.
[20] Y.Jiang,A.Gupta,Z.Zhang,G.Wang,Y.Dou,Y.Chen,L.Fei-Fei,A.Anandkumar,Y.Zhu,
and L. Fan. Vima: General robot manipulation with multimodal prompts. arXiv preprint
arXiv:2210.03094,2022.
[21] J.Schrittwieser,I.Antonoglou,T.Hubert,K.Simonyan,L.Sifre,S.Schmitt,A.Guez,E.Lock-
hart, D. Hassabis, T. Graepel, et al. Mastering atari, go, chess and shogi by planning with a
learnedmodel. Nature,588(7839):604–609,2020.
[22] L. Espeholt, H. Soyer, R. Munos, K. Simonyan, V. Mnih, T. Ward, Y. Doron, V. Firoiu,
T. Harley, I. Dunning, et al. Impala: Scalable distributed deep-rl with importance weighted
actor-learnerarchitectures. arXivpreprintarXiv:1802.01561,2018.
[23] S. Sodhani, A. Zhang, and J. Pineau. Multi-task reinforcement learning with context-based
representations. InInternationalConferenceonMachineLearning,pages9767–9779.PMLR,
2021.
[24] L.Kaiser, M.Babaeizadeh, P.Milos, B.Osinski, R.H.Campbell, K.Czechowski, D.Erhan,
C.Finn,P.Kozakowski,S.Levine,etal. Model-basedreinforcementlearningforatari. arXiv
preprintarXiv:1903.00374,2019.
[25] J.Tobin, R.Fong, A.Ray, J.Schneider, W.Zaremba, andP.Abbeel. Domainrandomization
for transferring deep neural networks from simulation to the real world. In 2017 IEEE/RSJ
internationalconferenceonintelligentrobotsandsystems(IROS),pages23–30.IEEE,2017.
[26] M.Shridhar,L.Manuelli,andD.Fox. Cliport: Whatandwherepathwaysforroboticmanipu-
lation. InConferenceonRobotLearning,pages894–906.PMLR,2022.
[27] A. Handa, A. Allshire, V. Makoviychuk, A. Petrenko, R. Singh, J. Liu, D. Makoviichuk,
K. Van Wyk, A. Zhurkevich, B. Sundaralingam, et al. Dextreme: Transfer of agile in-hand
manipulationfromsimulationtoreality. In2023IEEEInternationalConferenceonRobotics
andAutomation(ICRA),pages5977–5984.IEEE,2023.
[28] K. Bousmalis, G. Vezzani, D. Rao, C. Devin, A. X. Lee, M. Bauza, T. Davchev, Y. Zhou,
A.Gupta,A.Raju,etal.Robocat:Aself-improvingfoundationagentforroboticmanipulation.
arXivpreprintarXiv:2306.11706,2023.
13

--- Page 14 ---
[29] H. F. Song, A. Abdolmaleki, J. T. Springenberg, A. Clark, H. Soyer, J. W. Rae, S. Noury,
A. Ahuja, S. Liu, D. Tirumala, et al. V-mpo: On-policy maximum a posteriori policy opti-
mizationfordiscreteandcontinuouscontrol. arXivpreprintarXiv:1909.12238,2019.
[30] A.Gupta,J.Yu,T.Z.Zhao,V.Kumar,A.Rovinsky,K.Xu,T.Devlin,andS.Levine. Reset-
free reinforcement learning via multi-task learning: Learning dexterous manipulation behav-
iors without human intervention. In 2021 IEEE International Conference on Robotics and
Automation(ICRA),pages6664–6671.IEEE,2021.
[31] T.Yu,S.Kumar,A.Gupta,S.Levine,K.Hausman,andC.Finn. Gradientsurgeryformulti-
tasklearning. AdvancesinNeuralInformationProcessingSystems,33:5824–5836,2020.
[32] A. Mandlekar, D. Xu, J. Wong, S. Nasiriany, C. Wang, R. Kulkarni, L. Fei-Fei, S. Savarese,
Y. Zhu, and R. Mart´ın-Mart´ın. What matters in learning from offline human demonstrations
forrobotmanipulation. InConferenceonRobotLearning,pages1678–1690.PMLR,2022.
[33] E.Jang,A.Irpan,M.Khansari,D.Kappler,F.Ebert,C.Lynch,S.Levine,andC.Finn. Bc-z:
Zero-shottaskgeneralizationwithroboticimitationlearning. InConferenceonRobotLearn-
ing,pages991–1002.PMLR,2022.
[34] S. Dasari, J. Wang, J. Hong, S. Bahl, Y. Lin, A. Wang, A. Thankaraj, K. Chahal, B. Calli,
S. Gupta, et al. Rb2: Robotic manipulation benchmarking with a twist. arXiv preprint
arXiv:2203.08098,2022.
[35] K.Grauman,A.Westbury,E.Byrne,Z.Chavis,A.Furnari,R.Girdhar,J.Hamburger,H.Jiang,
M. Liu, X. Liu, et al. Ego4d: Around the world in 3,000 hours of egocentric video. In
ProceedingsoftheIEEE/CVFConferenceonComputerVisionandPatternRecognition,pages
18995–19012,2022.
[36] J.Deng,W.Dong,R.Socher,L.-J.Li,K.Li,andL.Fei-Fei. Imagenet: Alarge-scalehierar-
chicalimagedatabase. In2009IEEEconferenceoncomputervisionandpatternrecognition,
pages248–255.Ieee,2009.
[37] S.Nair,A.Rajeswaran,V.Kumar,C.Finn,andA.Gupta. R3m: Auniversalvisualrepresen-
tationforrobotmanipulation. arXivpreprintarXiv:2203.12601,2022.
[38] S.Parisi, A.Rajeswaran, S.Purushwalkam, andA.Gupta. Theunsurprisingeffectivenessof
pre-trainedvisionmodelsforcontrol. arXivpreprintarXiv:2203.03580,2022.
[39] A. Majumdar, K. Yadav, S. Arnaud, Y. J. Ma, C. Chen, S. Silwal, A. Jain, V.-P. Berges,
P.Abbeel,J.Malik,etal.Whereareweinthesearchforanartificialvisualcortexforembodied
intelligence? arXivpreprintarXiv:2303.18240,2023.
[40] R.ShahandV.Kumar.Rrl:Resnetasrepresentationforreinforcementlearning.arXivpreprint
arXiv:2107.03380,2021.
[41] M. Sharma, C. Fantacci, Y. Zhou, S. Koppula, N. Heess, J. Scholz, and Y. Aytar. Lossless
adaptationofpretrainedvisionmodelsforroboticmanipulation. InTheEleventhInternational
ConferenceonLearningRepresentations.
[42] N. Hansen, Z. Yuan, Y. Ze, T. Mu, A. Rajeswaran, H. Su, H. Xu, and X. Wang. On pre-
training for visuo-motor control: Revisiting a learning-from-scratch baseline. arXiv preprint
arXiv:2212.05749,2022.
[43] S.Tellex,T.Kollar,S.Dickerson,M.Walter,A.Banerjee,S.Teller,andN.Roy.Understanding
naturallanguagecommandsforroboticnavigationandmobilemanipulation. InProceedings
oftheAAAIConferenceonArtificialIntelligence,volume25,pages1507–1514,2011.
[44] C. Lynch and P. Sermanet. Language conditioned imitation learning over unstructured data.
arXivpreprintarXiv:2005.07648,2020.
14

--- Page 15 ---
[45] S. Stepputtis, J. Campbell, M. Phielipp, S. Lee, C. Baral, and H. Ben Amor. Language-
conditionedimitationlearningforrobotmanipulationtasks. AdvancesinNeuralInformation
ProcessingSystems,33:13139–13150,2020.
[46] A.Brohan,Y.Chebotar,C.Finn,K.Hausman,A.Herzog,D.Ho,J.Ibarz,A.Irpan,E.Jang,
R. Julian, et al. Do as i can, not as i say: Grounding language in robotic affordances. In
ConferenceonRobotLearning,pages287–318.PMLR,2023.
[47] A. Nguyen, D. Kanoulas, L. Muratore, D. G. Caldwell, and N. G. Tsagarakis. Translating
videos to commands for robotic manipulation with deep recurrent neural networks. In 2018
IEEEInternationalConferenceonRoboticsandAutomation(ICRA),pages3782–3788.IEEE,
2018.
[48] H. Bharadhwaj, A. Gupta, and S. Tulsiani. Visual affordance prediction for guiding robot
exploration. In 2023 IEEE International Conference on Robotics and Automation (ICRA),
2023.
[49] Y. Zhou, Y. Aytar, and K. Bousmalis. Manipulator-independent representations for visual
imitation. arXivpreprintarXiv:2103.09016,2021.
[50] L. Shao, T. Migimatsu, Q. Zhang, K. Yang, and J. Bohg. Concept2robot: Learning manip-
ulation concepts from instructions and human demonstrations. The International Journal of
RoboticsResearch,40(12-14):1419–1434,2021.
[51] K. Shaw, S. Bahl, and D. Pathak. Videodex: Learning dexterity from internet videos. In
ConferenceonRobotLearning,pages654–665.PMLR,2023.
[52] H. Bharadhwaj, A. Gupta, S. Tulsiani, and V. Kumar. Zero-shot robot manipulation from
passivehumanvideos. arXivpreprintarXiv:2302.02011,2023.
[53] S. Bahl, A. Gupta, and D. Pathak. Human-to-robot imitation in the wild. arXiv preprint
arXiv:2207.09450,2022.
[54] S.Bahl,R.Mendonca,L.Chen,U.Jain,andD.Pathak. Affordancesfromhumanvideosasa
versatilerepresentationforrobotics. arXivpreprintarXiv:2304.08488,2023.
[55] K.Rao,C.Harris,A.Irpan,S.Levine,J.Ibarz,andM.Khansari. Rl-cyclegan: Reinforcement
learningawaresimulation-to-real. InProceedingsoftheIEEE/CVFConferenceonComputer
VisionandPatternRecognition,pages11157–11166,2020.
[56] I.Kapelyukh,V.Vosylius,andE.Johns. Dall-e-bot: Introducingweb-scalediffusionmodels
torobotics. arXivpreprintarXiv:2210.02438,2022.
[57] M.Minderer,A.Gritsenko,A.Stone,M.Neumann,D.Weissenborn,A.Dosovitskiy,A.Ma-
hendran,A.Arnab,M.Dehghani,Z.Shen,etal.Simpleopen-vocabularyobjectdetectionwith
visiontransformers. arXivpreprintarXiv:2205.06230,2022.
[58] D. P. Kingma and M. Welling. Auto-encoding variational bayes. arXiv preprint
arXiv:1312.6114,2013.
[59] A.Vaswani,N.Shazeer,N.Parmar,J.Uszkoreit,L.Jones,A.N.Gomez,Ł.Kaiser,andI.Polo-
sukhin. Attention is all you need. Advances in neural information processing systems, 30,
2017.
[60] C. Mitash, F. Wang, S. Lu, V. Terhuja, T. Garaas, F. Polido, and M. Nambi. Armbench: An
object-centricbenchmarkdatasetforroboticmanipulation. arXivpreprintarXiv:2303.16382,
2023.
[61] F.Ebert,C.Finn,A.X.Lee,andS.Levine.Self-supervisedvisualplanningwithtemporalskip
connections. CoRL,12:16,2017.
15

--- Page 16 ---
[62] A. Kirillov, E. Mintun, N. Ravi, H. Mao, C. Rolland, L. Gustafson, T. Xiao, S. Whitehead,
A.C.Berg,W.-Y.Lo,etal. Segmentanything. arXivpreprintarXiv:2304.02643,2023.
[63] J. Yang, M. Gao, Z. Li, S. Gao, F. Wang, and F. Zheng. Track anything: Segment anything
meetsvideos. arXivpreprintarXiv:2304.11968,2023.
[64] E.Perez,F.Strub,H.DeVries,V.Dumoulin,andA.Courville. Film: Visualreasoningwitha
generalconditioninglayer. InProceedingsoftheAAAIConferenceonArtificialIntelligence,
volume32,2018.
[65] S. Y. Gadre, M. Wortsman, G. Ilharco, L. Schmidt, and S. Song. Clip on wheels: Zero-shot
object navigation as object localization and exploration. arXiv preprint arXiv:2203.10421,
2022.
[66] S.Haddadin,S.Parusel,L.Johannsmeier,S.Golz,S.Gabl,F.Walch,M.Sabaghian,C.Ja¨hne,
L. Hausperger, and S. Haddadin. The franka emika robot: A reference platform for robotics
researchandeducation. IEEERobotics&AutomationMagazine,29(2):46–64,2022.
[67] V. Kumar and E. Todorov. Mujoco haptix: A virtual reality system for hand manipulation.
In 2015 IEEE-RAS 15th International Conference on Humanoid Robots (Humanoids), pages
657–663.IEEE,2015.
[68] N.M.M.Shafiullah,Z.J.Cui,A.Altanzaya,andL.Pinto. Behaviortransformers: Cloningk
modeswithonestone. arXivpreprintarXiv:2206.11251,2022.
[69] J. Devlin, M.-W. Chang, K. Lee, and K. Toutanova. Bert: Pre-training of deep bidirectional
transformersforlanguageunderstanding. arXivpreprintarXiv:1810.04805,2018.
16

--- Page 17 ---
HeatSoup ServeSoup BakingPrep MakingTea CleaningUp StowBowl
Flap-OpenOven Flap-OpenOven Slide-OpenDrawer UncapLid PickLid Slide-OpenDrawer
PickBowl PickBowl PickButter PlaceLid CapLid PickBowl
Slide-InBowl Slide-OutBowl placeButter PickTea Slide-CloseDrawer PlaceBowl
Flap-CloseOven Flap-CloseOven Slide-CloseDrawer PlaceTea Flap-CloseOven Slide-CloseDrawer
PickLid PickTowel
Table2: Listofactivities(TopRow)andtheassociatedtasksforeachactivity.
A Datasetdetails
MT-ACT uses 7,500 human teleoperated demonstrations from the RoboSet dataset 3. MT-ACT
dataset consisted of RGB and depth frames from four camera views (right, left, top, and wrist) as
showninfigure6,Frankajointpositionsandvelocities,end-effector/gripperpositionandvelocities,
controlsappliedtotheFrankajointsandend-effector/gripper,andthetime-steps(40steps).
The data was collected using an Oculus Quest 2 controller on a kitchen table-top setup at 5Hz
and saved in HDF5 format. Rollouts from the data are shown in Figure 11 as well as in https:
//robopen.github.io/roboset/.
A.1 DatasetTerminology
SkillDifferentworksinroboticsoftenassigndifferentmeaningswhentheyreferto“skills”. Inour
work,werefertoaskillwhentherobotperformsasimilarmotionacrossdifferentobjectinstances
(bothshapeandsize).Forinstance,pick,place,open,closeobjectsareconsideredasdifferentskills.
Sinceourdatasetcontainsarticulatedobjectsifthe“open”skillwithmultipleobjectsresultsindif-
ferentmotionweclassifythemasdifferentskills. Forinstance,“OpenDrawer”requiresinteracting
withaprismaticjointwhile“OpenOven”interactswitharevolutejoint. Hence,weclassifytheseas
separateskills. Ourdefinitionisbroadlysimilartosomepreviousworks[5]. Weuse12skillsinRo-
boSet–Slide-Open, Slide-Close, Flap-Open, Flap-Close, Cap, Uncap, Pick, Place, Wipe, Plunge,
Slide-in,Slide-out.
Task: Wedefineeachinstantiationofourskillwithaparticularobjectclassasadifferenttask. For
instance, “Pick Mug” and “Pick Butter” correspond to the same “Pick” skill but are two different
tasks.
Activity: Ageneralrobotagentwilleventuallyneedtoperformasequenceoftasks,e.g. maketea.
Werefertosuchsequenceoftasksasactivities. Table2liststheactivitiesusedinourworkaswell
astaskscorrespondingtoeachactivity. Ourfinalaimistotrainasinglerobotagenttoperformall
activities.
Policies:Wetrainandcomparedifferentpoliciesinourwork.Weclassifythesepoliciesintosingle-
taskpolicy,multi-task(single-activity)andmulti-task(universal)policies. Aseachnamesuggests,
single-taskpoliciesaretrainedonspecifictasks. Multi-Task(single-activity)policiesaretrainedon
alltasksbelongingtoanactivity. Finally,Multi-Task(universal)policiesaretrainedonalltasksand
activities. OurfinalRoboAgentistrainedasaMulti-Task(universal)policy.
A.2 DetailsonSemanticAugmentations
Weenabletwodifferenttypesofsceneaugmentationsformultiplyingdata,forenablinggeneraliza-
tiontodifferentsceneswithnoveldistractors,andtosceneswithdifferentobjectsforinteraction:
• Augmentinginteractionobject: Giventhejointangleoftherobotinaframeofatrajectory,we
useforwardkinematicstorecovertherobotmaskaswellastheend-effectorpositionoftherobot.
3ThefullRoboSetismuchmorediverseandconsistsof9,500teleoperateddemonstrations,20,500kines-
theticdemonstrationsinvariouskitchenandtable-topsettings.Inaddition,itcontainsabout70,000trajectories
inbinsettingscollectedthroughheuristics
17

--- Page 18 ---
Figure11:SampletaskdemonstrationsintheRoboSet(visualizingfourviewshorizontally,andfivetimesteps
vertically),usedfortraining.
We use the end-effector location to prompt SegmentAnything [62] for obtaining a mask of the
objectbeinginteractedwith. Wetheninpainttheregionoftheobjectbeinginteractedwith,based
onatextprompt,andkeepitconsistentacrosstimebytrackingwithTrackAnything[63].
• Augmentingbackground: WeuseSegmentAnything[62]torandomlychooseasetofobjectsin
thebackgroundthatdonotoverlapwiththerobotmask,andthemaskoftheobjectbeinginteracted
with, andinpaintthescenebasedontheresultingoverallmaskoveralltheobjectsidentifiedby
SegmentAnything.
Note that our augmentation approaches are all automatic and do not require any manual effort in
specifyingmasksorobjectmeshesetc. Thisisincontrasttopriorworksthatrequiremanualspec-
ification of a fixed mask per trajectory [9], and those that require templates of object textures and
meshes[8]. Inaddition,unlike[10],wedonotrequiretraininganyfurthermodulesforidentifying
objectsthroughopen-vocabularydetectionthatreliesonlanguagegrounding.
B TrainandEvaluationDetails
Inthissectionwepresenttrainingandevaluationdetailsbothforourmethodsandthebaselines.
B.1 RobotEnvironmentandEvaluationDetails
Therobotenvironmentsforevaluationconsistoftable-topkitchensetupswithdiverserealobjects
inthescene. Thereare4camerasprovidingcomplementaryviewsoftheworkspace. Therobotisa
FrankaEmikaPandaarmoperatedwithjointpositioncontrol,withanactionspacedimensionof8
(7jointpositions,1dimensionforend-effectoropen/close). Therobotarmhasatwo-fingergripper,
andawristcamera. Therobotisoperatedatafrequencyof5Hz.
B.2 Hyper-parametersforMT-ACTandbaselines
Here we provide hyper-parameter details of the policy architecture. We train all policies for 2000
epochs. FortheoverallMT-ACTagent,trainedontheaugmenteddataset,thistakesabout48hours
onasingle2080TiGPUwithabatchsizeof8.
18

--- Page 19 ---
Figure12: QualitativeresultsofrolloutsforL2andL3levelsofgeneralization,showingtasksopendrawer
andpickaslabofbutter. ForL2weintroducedifferentdistractorsinthescene,andchangethebackground
tiles. ForL3,inadditiontochangesinL2weintroducedifferenttaskobjects,forexamplebyreplacingaslab
ofbutterwithapieceofwatermelon,orabanana.
Table3: Hyper-parametersforMT-ACT
Table4: Hyper-parametersforRT-1[5]
Name Value
Name Value
learningrate 1e-5
learningrate 1e-4
batchsize 8
discreteactiontokens 256
feedforwardsize 3200
batchsize 64
Attentionheads 8
feedforwardsize 1024
chunksize 20
Attentionheads 8
dropout 0.1
dropout 0.1
Transformerencoderlayers 4
Transformerlayers 6
Transformerdecoderlayers 7
LanguageEmbeddingsize 384
LanguageEmbeddingsize 384
Forourbaselineimplementationswedidahyperparametersearchforrelevantparameters. Foreach
baselineimplementationwetrytoadaptthemfromtheirofficiallyreleasedcode. Specificially,for
RT1 [5] we use https://github.com/google-research/robotics_transformer for refer-
ence. Ontheotherhand,forBET[68]weusehttps://github.com/notmahi/bet. Toprovide
languageconditioningforbothbaselinesweusesimilarFiLM[64]implementationasourapproach.
Forhyper-parametersweuse3differentdiscreteactionsizes–64,256and512,wevarythelearning
ratesfrom(1e−3,1e−4).WeusetheAdamWoptimizerwithaweightdecayrangein(1e−2,1e−
3,1e−4). OurRT-1transformeruses6layerswith8parallelattentionheadsandeachheadwith
size 64. Each transformer uses a feedforward layer with intermediate sie of 1024. On the other
hand for [68] we experiment with 3 different action cluster sizes – 64, 256 and 512. We use a
similartransformerimplementationforBETasRT-1. Finally,forreal-worldevaluationweusethe
hyper-parameterswithlowestvalidationloss.
C AdditionalResults
In this section, we present some additional results. First, we present results and discuss how well
ourmulti-taskpolicyperformswhencomparedtosingle-taskpolicies. Figure13comparessingle-
task policy performance against two sets of multi-task policies for the Heat Soup activity. For the
firstmulti-taskSingle-Activitypolicy(MTSingle-Activity)weonlytrainitacrossalltaskswithin
the same activity. For the latter multi-task universal multi-activity policy (MT-Universal) we train
itacrossalltasksinallactivities. FromFigure13weseethatformosttasksMTSingle-Activityis
able to outperform single task policies. Additionally, single-task policies are able to perform well
onmosttasks(≈80%)exceptthemorechallengingconstrainedmanipulationtasks(slide-in-bowl)
(≈ 20%). Finally,wealsoobservethatMT-Single-ActivitycanoutperformMT-Universalformost
tasks. Thishappensbecausetheuniversalagentistrainedtoperformamuchlargervarietyoftasks.
Giventheverylargevarietyofskills(Figure3),suchmulti-tasktrainingcanresultinsomenegative
19

--- Page 20 ---
100
80
60
40
20
0
Flap-Open Oven Pick Bowl Slide-In Bowl Flap-Close Oven
Single-Task Multi-Task (Single-Activity) Universal (Multi-Activity)
Figure13: Single-TaskvsMulti-TaskcomparisonforHeatSoupactivity. Multi-Task(SingleActivity)repre-
sentsamulti-taskpolicytrainedononly4tasksinHeat-Soupactivity.
transfer compared to training on a narrowly defined skills. We believe these reduced multi-task
resultspresentusefulavenuesforfutureresearch. Finally, inTable5weshowresultsforalltasks
in all activities using our single universal policy. From the below table, we see that the universal
policy is able to perform well on most tasks except the more challenging tasks such as grasping
smalldeformableobjects(PickTea: 40%,PickLid: 50%).
HeatSoup Success ServeSoup Success BakingPrep Success
Flap-OpenOven 80% Flap-OpenOven 90% Slide-OpenDrawer 70%
PickBowl 60% PickBowl 50% PickButter 70%
Slide-InBowl 70% Slide-OutBowl 80% placeButter 90%
Flap-CloseOven 50% Flap-CloseOven 80% Slide-CloseDrawer 90%
MakingTea Success CleaningUp Success StowBowl Success
UncapLid 80% PickLid 70% Slide-OpenDrawer 70%
PlaceLid 90% CapLid 100% PickBowl 70%
PickTea 40% Slide-CloseDrawer 90% PlaceBowl 80%
PlaceTea 60% Flap-CloseOven 80% Slide-CloseDrawer 80%
PickLid 50% PickTowel 90%
CapLid 70% WipeCounter 90%
Table5: Resultsfordifferenttasksusingthelearneduniversalpolicy.
20