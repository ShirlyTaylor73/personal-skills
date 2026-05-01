--- Page 1 ---
RoboTwin 2.0: A Scalable Data Generator and
Benchmark with Strong Domain Randomization for
Robust Bimanual Robotic Manipulation
TianxingChen2,16*† ,ZanxinChen3,5*,BaijunChen15*,ZijianCai3,5*,YibinLiu13*,
ZixuanLi5*,QiweiLiang5,XianliangLin5,YihengGe1,ZhenyuGu7,8,WeiliangDeng3,11,
YubinGuo7,9,TianNian3,5,XuanbingXie12,QiangyuChen5,KailunSu5,TianlingXu10,
GuodongLiu6,7,MengkangHu2,Huan-angGao6,16,KaixuanWang2,16,
ZhixuanLiang2,3†,YusenQin4,6,XiaokangYang1,PingLuo2,14(cid:66),YaoMu1,3(cid:66)†
1MoEkeyLabofArtificialIntelligence,AIInstitute,SJTU‡,2HKUMMLab‡,
3ShanghaiAILab,4D-Robotics,5SZU,6THU,7TeleAI,8FDU,9USTC,10SUSTech,
11SYSU,12CSU,13NEU,14HKU-SHICRC,15NJU,16LuminaEAI
*Equalcontribution (cid:66)Correspondingauthors †Co-projectleads
‡Equallyleadingorganizations
Webpage:https://robotwin-platform.github.io Doc: https://robotwin-platform.github.io/doc/
50 Dual-arm Tasks Rich Diversity
731 Diverse Objects Benchmark
5 Embodiments LargeDataset Scale
Performance Domain Randomization Unseen Real-World OpenSource
Sim2Real
42%
4.7x 30% Randomization
9% RoboTwinObject Dataset
Only Real-World Zero-shot Few-shot
Community LeaderBoard
Auto Code Generation
71.3% (ours) Generate Any Dual-Arm Robot ManipData DeployDiverse Policies
60.4% 63.9%
Pre-Collected 100k+ Traj.
RoboTwin1.0 Vanilla
47.4% R R o o b b o o T T w w i i n n 1 1 . . 0 0 + + F F B B+MLLM Friendly Codes&Tutorial
RoboTwin2.0
Figure1: OverviewofRoboTwin2.0. RoboTwin2.0isascalableframeworkforbimanualmanipu-
lation,integratinganexpertdatagenerationpipelinewitha50-taskbenchmarkbuiltontheRoboTwin
ObjectDataset(731objects,147categories). Amultimodallanguageagentautomatestaskprogram
synthesis,whileflexibledual-armconfigurationsenablelarge-scale,diversedatacollection. Policies
trainedonRoboTwin2.0exhibitimprovedrobustnessandgeneralizationtounseenenvironments.
Abstract
Simulation-baseddatasynthesishasemergedasapowerfulparadigmforenhanc-
ingreal-worldroboticmanipulation. However,existingsyntheticdatasetsremain
insufficientforrobustbimanualmanipulationduetotwochallenges: (1)thelack
ofanefficient,scalabledatagenerationmethodfornoveltasks,and(2)oversim-
plified simulation environments that fail to capture real-world complexity. We
presentRoboTwin2.0,ascalablesimulationframeworkthatenablesautomated,
5202
guA
72
]OR.sc[
2v88081.6052:viXra

--- Page 2 ---
large-scalegenerationofdiverseandrealisticdata,alongwithunifiedevaluation
protocolsfordual-armmanipulation. WefirstconstructRoboTwin-OD,alarge-
scaleobjectlibrarycomprising731instancesacross147categories,eachannotated
withsemanticandmanipulation-relevantlabels. Buildingonthisfoundation,we
developanexpertdatasynthesispipelinethatcombinesmultimodallargelanguage
models(MLLMs)withsimulation-in-the-looprefinementtogeneratetask-level
execution code automatically. To improve sim-to-real transfer, RoboTwin 2.0
incorporatesstructureddomainrandomizationalongfiveaxes: clutter, lighting,
background, tabletop height and language instructions, thereby enhancing data
diversityandpolicyrobustness. Weinstantiatethisframeworkacross50dual-arm
tasksspanningfiverobotembodiments. Empiricalevaluationshowsa10.9%gain
incodegenerationsuccessrate. Buildingonthis,weevaluatedownstreampolicy
learning. Withamixoflarge-scalesyntheticdataandonly10realdemonstrations,
avision–language–action(VLA)modelachievesa367%relativeimprovement
overthe10-demobaseline. Evenwithoutrealdata,zero-shotmodelstrainedsolely
on synthetic data obtain a 228% relative gain, highlighting the effectiveness of
ourdatasetinstrengtheningsim-to-realtransferandrobustnesstoenvironmental
variations. Wereleasethedatagenerator,benchmark,pre-collecteddataset,and
codetosupportscalableresearchinrobustbimanualmanipulation.
1 Introduction
Bimanualroboticmanipulationiscriticalforenablingrobotstoperformcomplexreal-worldtasks
suchascollaborativeassembly,tooluse,andobjecthandovers. Developinggeneralizablebimanual
policies—particularlyvision–language–action(VLA)foundationmodels—requiresdatasetsthatare
simultaneouslyhigh-quality,diverse,andlarge-scale. Intheabsenceofsufficientvariabilityinobject
geometry,sceneclutter,lightingconditions,instructionlanguage,androbotembodiments,learned
policiesoftenoverfittonarrowdistributionsandfailtogeneralizetonovelenvironmentsorhardware
platforms. Yetcollectingreal-worlddemonstrationsatscaleremainsprohibitivelyexpensive,time-
consuming,andlogisticallychallenging,especiallywhenaimingtocoverabroadrangeoftasks,
objects,andembodiments.
Simulation-baseddatagenerationprovidesascalablealternativeforcollectinglarge-scalemultimodal
datasetsandhasshownpromiseinenablingsim-to-realtransfer[34,11]. However,existingpipelines
fallshortinthreecriticalaspects. First,theylackautomatedqualitycontrol: withoutanexpert-level
validationloop,manygeneratedtrajectoriesincludeexecutionfailuresorsuboptimalgrasps,which
degradepolicylearning. Second,theirdomainrandomizationisoftensuperficial,yieldingoverly
cleanandhomogeneousscenesthatomitessentialreal-worldfactorssuchasclutter,lightingvariation,
andambiguouslanguageinstructions—elementscrucialforrobustsim-to-realtransfer. Third,they
overlookcross-embodimentvariation: differentbimanualplatformscandiffersubstantiallyintheir
kinematiccapabilitiesandgraspstrategies. Forexample,alow-degree-of-freedom(DoF)platform
likethePiperoftenreliesonlateralgraspsduetoitslimiteddexterity,whereasahigh-DoFarmsuch
astheFrankaiscapableoftop-downprecisiongrasps. Yet,currentsyntheticdatasetsrarelyencode
suchembodiment-specificaffordancesortaskconstraints,limitingtheirgenerality.
Toaddressthesechallenges,weintroduceRoboTwin2.0,ascalablesimulation-baseddatageneration
framework designed to produce high-quality, diverse, realistic, and interaction-rich datasets for
bimanualmanipulation. RoboTwin2.0integratesthreekeycomponents: (1)anautomatedexpert
datagenerationpipelinethatleveragesmultimodallargelanguagemodels(MLLMs)andsimulation-
in-the-loopfeedbacktoiterativelyvalidateandrefinetaskexecutioncode;(2)comprehensivedomain
randomizationoverlanguageinstructions,objectclutter,backgroundtextures,lightingconditions,
andtabletopconfigurations,aimedatclosingthesim-to-realgapandenhancingpolicygeneralization;
and(3)embodiment-awareadaptation,inwhichobjectaffordancesareannotatedandrobot-specific
actioncandidatesaregeneratedtoaccountforheterogeneousdual-armkinematics.
Building on these components, we introduce three new resources to support scalable research
in bimanual manipulation: (1) the RoboTwin-OD asset library, comprising 731 annotated object
instances across 147 categories; (2) an automated data generation pipeline with comprehensive
domainrandomizationandacollectionofover100,000experttrajectoriesspanning50tasksacross
fivedual-armrobotplatforms;and(3)abenchmarkforevaluatingpolicygeneralizationtocluttered
2

--- Page 3 ---
environments and open-ended language goals. Together, these resources enable the community
to train and evaluate robust bimanual manipulation policies under conditions that closely reflect
real-worldcomplexityanddiversity.
In summary, our main contributions are as follows: (1) We develop an automated expert data
generation framework that integrates multimodal large language models with simulation-in-the-
loopfeedbacktoensurehigh-quality,expert-leveltrajectories;(2)Weproposeasystematicdomain
randomizationstrategythatenhancespolicyrobustnessbyincreasingdatadiversityandsim-to-real
generalization;(3)Weintroduceanembodiment-awareadaptationmechanismthatgeneratesrobot-
specific manipulation candidates based on object affordances; (4) We release the RoboTwin-OD
assetlibrary,alarge-scalepre-collectedmulti-embodimentdomain-randomizedtrajectorydataset,a
scalablebimanualdatagenerator,andastandardizedevaluationbenchmarktosupportscalabletraining
andevaluationofgeneralizablepoliciesacrossdifferentrobotembodiments,sceneconfigurations,
andlanguageinstructions.
2 Method
Language Description
Place the toy-car in basket and move basket
Auto Expert Data Collection Code Gen
Images and
Code Exec Cluttered Table, Background, Light, Tabletop Height, Instruction Error Feedback
GeneralizetoUnseen Scene
Robust Robot ManipulationPolicyTraining
niamoD
/w
noitazimodnaR
ExpertData Collection
RoboTwin-OD API Library
Training
Observation Retrieval
MLLM
Figure 2: RoboTwin 2.0 Pipeline. Built on RoboTwin-OD and a skill API, the framework uses
MLLM-basedcodegenerationwithsimulationfeedbacktoproduceexperttaskprogramsanddomain-
randomizedtrajectoriesforpolicytrainingandevaluation.
WeillustratetheoverallRoboTwin2.0pipelineinFig.2. Theframeworkbeginswithataskcode
generationmodulethatleveragesmultimodallargelanguagemodels(MLLMs)andsimulation-in-the-
loopfeedbacktoautomaticallysynthesizeexecutabletaskplansfromnaturallanguageinstructions.
Thismoduleisgroundedonalarge-scaleobjectassetlibrary(RoboTwin-OD)andapredefinedskill
library,enablingscalabletaskinstantiationacrossabroadrangeofobjectcategoriesandmanipulation
scenarios. To ensure high-quality expert demonstrations, we integrate this automated generation
pipeline with RoboTwin 2.0’s comprehensive domain randomization scheme, which diversifies
observationsalonglanguage,visual,andspatialaxes. Thispipelinesupportsthesynthesisofdiverse
andrealistictrainingdata,facilitatingthedevelopmentofmanipulationpoliciesthatarerobustto
real-worldenvironmentalvariability.
2.1 ExpertCodeGenerationviaMLLMsandSimulation-in-the-LoopFeedback
Recentadvancesinlanguagemodelsshowstrongabilitytogenerateintermediatetaskrepresenta-
tions—suchastextualplans[18],APIcalls,orexecutablecode[33,6,19]—forcomplexrobotic
tasks. Multimodallargelanguagemodels(MLLMs)furtherextendthiscapabilitybyincorporating
visualandproprioceptiveinputs,enablingmoregroundedreasoningoverreal-worldsensorydata.
However,priorsystemsoftendependonstrongmanualpriorsorlackclosed-loopfeedbackduring
programsynthesis,whichlimitstheirrobustnessindiverseordynamicenvironments.
Toaddresstheselimitations,weproposeanautomatedexpertdatagenerationpipelinethatintegrates
programmatic code synthesis with multimodal execution feedback (Fig.3). The system adopts a
closed-loop architecture with two agents: a code-generation agent and a vision–language model
(VLM)observer. Thecodeagentsynthesizestaskprogramsfrominstructions,whiletheobserver
monitorsexecutioninsimulation,detectsfailures,andsuggestscorrections. Thisiterativefeedback
3

--- Page 4 ---
loopenablesthecodeagenttorefineprogramsautomatically,producingrobust,self-improvingexpert
datawithminimalhumansupervision. UnlikepriorMLLM-basedpipelinessuchasGenSim2[20]
andRoboGen[43],oursystemsupportszero-shotgenerationofcomplexdual-armbehaviorsbeyond
primitivepick-and-placeactions.
Iterations
> 5
Han T E F d A a u x o P s a n v I k m c e L t i r i p n i o s l B f n e t o l ock CodeAgent de s #l#ss#hst #ssss#tstcs f e e a a a ee e eeee e eo S a p l fI S S S ll l llll l l r r r f n n t t ff f ffff f f nl . t t t g g g _ e a .. . s .... . .s d e e e i m m m ms mm s s e e e pa t a yt p p p a a a o r t t t i v r _ o oo o o o a _ _ _ v v v 3 v a 1 2 4 m e o v vv v v v l p p p e e e : e i _ i : : : n n e ee _ _ _ e e e r z o o o U o U M M = = c ( (( ( ( ( _ e o o o s s s b s s sss s s e p e e e“ b b b s a e e eee e A e o o ( s= = e f o s s s l l lll l h = r e v v r r f f fff f r e e e h t s m l r a . . ... . e e e m a i r r r e eg p gco sp avg n e v v v r f e l r r p b b l l n = ah ” o Tt td a ag l a a a a a e a o of dt ) s t a c c o e a t t t s . s s n i ) g x x e o t i i i e e o t a r v e p p g o o o a __ s _ v_ _ m nr lt t e ( _ _ n n n r gg f p o o ea a m " r ( . a a g ( ( ( rr rs b o c c _ lt s s s h t c c e ii t e _ t ts o l b a pp t t t t t t e t aoo o f p e e e e o o o r_ l pp p tg ncr r, o p p p o " g r r b ee _g k r ( (f d c _ _ _ s ( ( e ) a a rr u o a nr _ a a k e o , n n n t (( c cx a n b a m , c c r ) v aa a a a b t t. s : c mf t t i e o o r g r t m m m g o p u o o i t h r mm r r d e i h x e r r n o e e e = =t e t dp = = = t c _ _ h _ n = = = u s s _ l b o t s s " t f t e ee ea " " " s i a e e u a i a o m _ ol l i n l l r b b l l r f f g nn g x _ e p f f n i t . . m o oo = . .= g b b f g c p o a b b f ut x xv t hl o oo r r s _ l r o o i e _ s = e_ i o x xo t e i i a f x xg i n p _ _g p m n , ,n t A r, ,h a t t a l _ h a o a g a m a _ o a r t r ra t r i r t l _ c i _ m r n l m m _ r om m _ d a e e am ht m p P p g = f d r __ r T _ a _ _ t o r m _ t _ 0 m i g) n t t a a i a d a t ) o , a an r d g a r g s ) r = n g a gt ) p o ( g m =1 ( = _ s = " v = s o 1 l p t l r r . _ e e , r e a . s i i f. b r i " f g g ) _ r t g g _ t ) o _ p g h h b _ h p x a e ot t o a t o _ " " t r r s _ x r " i a m ) e )m a " n ) "r a r ) t , m) " m . . ) . , m ) . ) ..)) Runx T E 1 a x s e 0 k c ! . Success Rate > 0.5 Code Pass
Code Repair History
Observation Execution Log
Step1 Step2 Execution success
Observe Select Error Unexecutable code
Left grasp failure
Step3 ! Step4 Fail
Right grasp failure
VLMAgent
Incorrect target position
Code Fail
Figure3: ExpertCodeGenerationPipeline.
Input Specification. Each task is defined by a task name (e.g., Handover Block) and a natural
languagedescriptionoftheobjective. Thecode-generationagentisconditionedonthreekeyinputs:
ageneralAPIlist,asetofexamplefunctioncalls,andahierarchicalconstraintspecification. These
componentscollectivelyguidethesynthesisofPythoncodetoexecutethetask. Additionally,each
taskmayincludetask-specificfunctioncallexamplestofurthergroundcodegenerationincontext.
InitialCodeGeneration. Thecode-generationagentsynthesizesaninitialPythonprogramcondi-
tionedontheprovidedtaskinputs. Itmodelstheprogramsynthesisprocessasastructuredprediction
problemoverthespaceofavailableAPIcalls,leveragingnaturallanguageunderstandingandfew-shot
promptingfromtask-specificexamples. Thegeneratedcodespecifiesastepwisesequenceofrobot
actionsdesignedtoaccomplishthetargetmanipulationobjective.
Simulated Execution and Logging. The generated program is executed ten times per iteration
withinasimulatedroboticenvironment. Multipletrialsareusedtoaccountforstochasticvariations
insimulationdynamics,robotcontrollers,andsensornoise. Aftereachexecutionbatch,thesystem
generatesastructuredexecutionlogthatrecordsthesuccessorfailureofeachtrialandannotates
failurecaseswiththeircorrespondingcauses—suchasunexecutablecode,left/rightgraspfailure,or
incorrectobjectplacement.
MultimodalObservationandErrorLocalization. Inparallelwithexecution,avision-language
model(VLM)agentobservestherobot’sbehavioracrossalltentrials. TheVLMperformsframe-
by-frameinspectiontoevaluatethesuccessofeachprogramstepandlocalizethepointoffailure
whenerrorsoccur. Beyondtemporallocalization,theVLMalsodiagnosesfailuremodesbyinferring
whethertheunderlyingcausestemsfromflawedlogic,incorrectAPIusage,orothersystemicissues.
Thisdiagnosticcapabilityenablesthesystemtoaddressrootcausesratherthanmerelyrespondingto
superficialexecutionerrors. ThedetailofVLMobservationisshowninG.4.
CodeRepairandIterativeRefinement. Thecode-generationagentreceivestwocomplementary
feedbacksignals: (i)aquantitativeexecutionlogand(ii)aqualitative, localizeddiagnosticfrom
the VLM. It integrates these inputs to revise the program by modifying or replacing instructions
identifiedasfailure-prone. Theupdatedprogramisthenre-evaluatedinthenextiteration,andthe
processcontinuesuntileithertheprogramachievesthesettingsuccessrateacrosstensimulatedruns
inoneiterationorfailstodosoafterfiveconsecutiverefinements. Thisloopyieldsexpert-leveltask
codewithminimalhumansupervisionwhileavoidingindefiniterefinement.
The outcome of this pipeline is a collection of robust, automatically synthesized programs that
generate high-quality expert trajectories for downstream training and evaluation. By integrating
multimodal reasoning with execution-level feedback, the system produces code that is not only
syntacticallycorrectbutalsosemanticallyalignedwithtaskobjectives. Thisclosed-loopgeneration
4

--- Page 5 ---
framework substantially reduces human supervision while enabling scalable and self-improving
expertdatacreationforcomplexroboticmanipulationtasks.
2.2 DomainRandomizationforRobustRoboticManipulation
Toenhancepolicyrobustnesstoreal-worldvariability,weapplydomainrandomizationalongfive
dimensions: (1) cluttered distractor objects, (2) background textures, (3) lighting conditions, (4)
tabletopheights,and(5)diverselanguageinstructions. Thissystematicaugmentationbroadensthe
trainingdistributionandmarkedlyimprovesgeneralizationtounseenscenarios. Theeffectsofthese
randomizationsarevisualizedinFig.4a.
Domain Randomization:
Fixed Scene Scene Clutter, Lighting, Table Height,Background and Language 11k Textures
(a) Visualization of Domain Randomization (b) Texture Library
Figure4: Visualizationofdomainrandomizationandourtexturelibrary.
Scene Clutter. To enhance robustness to environmental variation, we augment tabletop scenes
withtask-irrelevantdistractorsdrawnfromRoboTwin-OD(731objectsacross147categories;see
Section3.1). Eachobjectincludesplacementannotations,enablingagenericAPIforsemantically
valid insertion. We ensure physical plausibility via collision-aware placement and precomputed
volumes. To avoid policy confusion, distractors visually or semantically similar to task-relevant
objects are excluded during sampling. This yields diverse yet unambiguous cluttered scenes for
training.
Diverse Background Textures. We randomize tabletop surfaces and backgrounds using a large
curatedtexturelibrary. Tobuildit,wefirstcollected1,000diversesurfacedescriptionsviaLLM
promptingandwebcrawling,thenusedStableDiffusionv2togenerate20samplesperdescription
(20,000total). Afterhuman-in-the-loopfiltering,weobtained11,000high-qualitytextures. This
libraryisappliedinsimulationtoenrichvisualdiversityandreduceoverfittingtocleansynthetic
environments(seeFig.4b).
LightingVariation.Real-worldenvironmentsexhibitdiverseilluminationconditions,withvariations
incolortemperature, sourcetype, number, andplacement. Thesefactorsalterobjectappearance
andreflections,challengingvision-basedmanipulation. Toenhancerobustness,werandomizelight
color,type,intensity,andpositionwithinphysicallyplausiblebounds. AsshowninFig.4a(second
row),changesincolortemperaturecandrasticallyshiftobjectappearance(e.g.,ashoeunderwarm
vs. coollight). Trainingundersuchrandomizedconditionsimprovespolicyrobustnesstoreal-world
illuminationshifts.
Tabletop Heights. In practice, table heights vary across workspaces, affecting robot perception,
kinematics,andinteraction. Toimprovegeneralization,weuniformlyrandomizetableheightwithina
plausiblerangeduringsimulation,introducingvariabilityinviewpointsandspatialrelationsbetween
robotandobjects.
Trajectory-LevelDiverseLanguageInstructions. Toimproverobustnesstonaturallanguagevaria-
tion,weuseamultimodalLLMtogeneratediversetasktemplatesandmultipleobjectdescriptions
capturing geometry, appearance, and part-level attributes. Each task and object thus has several
alternativephrasings,whichcanbeflexiblycombined. Foreverytrajectory,wesamplefromthese
poolstocomposeinstructions. Forexample,inMoveCanPot,thetemplate“UseatoplaceAto
theleftofB”mayyielddiverseinstructionssuchas“Useleftarmtoplacesaucecantotheleftof
5

--- Page 6 ---
graykitchenpot”or“Useleftarmtoplacewhiteplasticlidsaucecantotheleftofkitchenpotfor
boilingandcooking.”Thiscombinatorialaugmentationproducesalargesetoflinguisticallyvaried
instructionsandsignificantlyimprovesgeneralizationtounseenlanguageandsceneconfigurations
(seeAppendixH,I).
2.3 Embodiment-AwareGraspAdaptation
DuetodifferencesinDoFandkinematicstructures,roboticarmsexhibitvaryingreachableworkspaces
and preferred manipulation strategies for the same task. For example, when grasping a can, the
Frankaarmtypicallyfavorsatop-downapproach,whilethelower-DoFPiperarmisbettersuitedto
sidegrasps. Asaresult,atasksuccessfullycompletedbyFrankausingatop-downgraspmayrequire
asideapproachwhenexecutedwithPiper,asshowninFig.6.
Aloha-AgileX ARX-X5 Piper Franka UR5
Figure6: DifferentGrasp-
Figure5: FiveRoboTwin2.0Embodiments.
ingBehavior.
To address embodiment-specific variations, we annotate each object with a rich set of candidate
manipulationposesthatcovermultiplegraspaxesandapproachdirections. Thisdesigncapturesboth
manipulationdiversityandrobot-specificpreferences. Tofurtherexpandthefeasiblespace,weapply
angularperturbationsbiasedtowarddirectionswithhigherarmreachability. Concretely,foreach
objectwegeneratecandidategraspsbycombiningpreferredoperationdirections,randomizedpose
perturbations,andparallelizedmotionplanningattempts.
3 RoboTwin2.0DataGenerator,BenchmarkandLargeScaleDataset
3.1 RoboTwin-OD:RoboTwinObjectDataset
Rich ManipulationAnnotation
Grasp Object Axis
Point
Functional
Point
041_shoe Diverse Language Annotation
base4
“green shoe”,“teal sneaker”,“rubber sole
running shoe”,“blue and green running
RoboTwin-OD shoe”,“half green half blue sneaker”,“teal
running shoe with thick beige sole”, etc
Figure7: RoboTwin-OD.Alarge-scaleobjectdatasetforroboticmanipulationwith147categories
and731objects,annotatedwithrichinteractionlabelsanddiverselanguagedescriptions.
Toenhancebothmanipulationcapabilityandvisualunderstanding,weconstructalarge-scaleobject
datasetwithrichsemanticannotations,calledRoboTwin-OD,covering147categoriesand731diverse
objects. Specifically,thisincludes534instancesacross111categoriesthatwegeneratedin-house
usingRGB-to-3DreconstructionviatheRodinplatform1,followedbyconvexdecompositionand
1https://hyper3d.ai/
6

--- Page 7 ---
meshmergingtoensurephysicallyaccuratecollisionmodels.Inaddition,RoboTwin-ODincorporates
153objectsfrom27categoriesinObjaverse[10],and44articulatedobjectinstancesfrom9categories
in SAPIEN PartNet-Mobility [48]. Objects from all sources, including Objaverse, are used to
constructclutteredscenes,withObjaversespecificallyenhancingthevisualandsemanticdiversityof
distractorobjects. Wealsodevelopacomprehensivetexturelibraryforsurfacesandbackgrounds
usinggenerativeAIandhuman-in-the-loopfilteringtoensurevisualrealismanddiversity.
Forrobustmanipulation,policiesmustgeneralizeacrossdiverseobjects,whichrequiresdatasets
with broad category coverage and varied intra-class instances. To facilitate language grounding,
we developed an automated object description generator with human verification, producing 15
annotationsperobjectthatvaryinshape,texture,functionality,partstructure,andgranularity.
To further support object-centric interaction, we annotate each object with key point–axis infor-
mation, including placement points, functional points, grasp points, and grasp axes, explicitly
encodingaffordances. TogetherwithourmanipulationAPIlibrary,theseannotationsenablegen-
eralizable grasp execution in simulation. All object information is available at http://robotwin-
platform.github.io/doc/objects/.
3.2 50TasksforDataGenerationandBenchmarking
Building on our automated task generation framework, embodiment-adaptive behavior synthe-
sis, and the large-scale RoboTwin-OD asset library, we construct a suite of 50+ dual-arm col-
laborative manipulation tasks. We further support data collection and evaluation on five dis-
tinct robot platforms, enabling comprehensive cross-embodiment benchmarking. Keyframes
from representative tasks are shown in Fig. 8, and the complete task descriptions are avail-
able at http://robotwin-platform.github.io/doc/tasks/. We also pre-collected over 100,000 dual-
arm manipulation trajectories across 50 tasks in RoboTwin 2.0, which are available at
https://huggingface.co/datasets/TianxingChen/RoboTwin2.0/tree/main/dataset.
Figure8: 50RoboTwin2.0BimanualManipulationTasks.
4 Experiment
We design experiments to evaluate the effectiveness of RoboTwin 2.0 in three key aspects: (1)
automatingthegenerationofhigh-qualityexpertcodeformanipulationtasks;(2)improvingpolicy
robustnesstoenvironmentalvariationviadiversifiedtrainingdata;and(3)demonstratingtheutility
and diversity of RoboTwin 2.0 as a standardized benchmark for evaluating policy generalization
acrosstasks,scenes,andembodiments.
4.1 EvaluationofAutomatedExpertCodeGeneration
Weevaluateourclosed-loopexpertdatagenerationsystemonasuiteof10roboticmanipulationtasks,
eachspecifiedwithanaturallanguageinstruction. Foreachconfiguration,thecode-generationagent
producesmultiplecandidateprograms,whichareexecutedinsimulationtoaccountforstochasticity
7

--- Page 8 ---
indynamics,control,andperception. Task-levelsuccessisdefinedastheaveragesuccessrateacross
allexecutions,asdescribedinSection2.1.
Table 1: Overall performance comparison across 1.0
RoboTwin variants. Evaluated on the subset of tasks
supportedbybothRoboTwin1.0andRoboTwin2.0. Per- 0.8
tasksuccessratecomparisonisprovidedinAppendix8. 0.6
0.4
Method ASR Top5-ASR CR-Iter Token
R1.0Vanilla 47.4% 57.6% 1.00 1236.6 0.2
R1.0+FB 60.4% 71.4% 2.46 1190.4
0.0
R1.0+MMFB 63.9% 74.2% 2.42 1465.0 R1.0 Vani R ll 1 a .0 + R F 1 B .0 + MM R2 F .0 B Vani R ll 2 a .0 + R F 2 B .0 + MM FB
R2.0Vanilla 62.1% 68.0% 1.00 569.4
R2.0+FB 66.7% 73.6% 1.89 581.6
R2.0+MMFB 71.3% 78.6% 1.76 839.7
etaR
sseccuS
Figure9: RoboTwinSuccessRateDis-
tribution.
Weevaluateperformancewithfourmetrics: ASR(AverageSuccessRate),Top5-ASR(successover
thetop-5candidatespertask),CR-Iter(averagerefinementiterationsbeforetermination),andToken
(averagenumberoftokensingeneratedpolicycode). ResultsonRoboTwin1.0and2.0arereported
inTable1underthreeconfigurations: Vanilla(one-shotcodegeneration),FB(feedback-basedrepair
viaexecutionlogs),andMMFB(multimodalfeedbackwithvision–languagediagnostics). Per-task
successratesareprovidedinAppendix8.
Acrossallsettings,multimodalfeedbackyieldsconsistentgains. InRoboTwin1.0,ASRimproves
from47.4%(Vanilla)to63.9%(MMFB);inRoboTwin2.0,itrisesfrom62.1%to71.3%. Improve-
mentsarealsoevidentinTop5-ASR,suggestingthatperceptualfeedbackdisproportionatelybenefits
thebestcandidateprograms. RoboTwin2.0convergesfasterthan1.0(e.g.,1.76vs.2.42CR-Iterin
MMFB),indicatingstrongerpriorsandmoreefficientrefinement. Tokencostisalsosubstantially
reduced,especiallyinVanilla(569.4vs.1236.6),reflectingmoreconciseinitialcode.
Figure9furthershowsthatfeedbacknarrowsthesuccess-ratedistributionandraisesthemedian.
RoboTwin2.0withmultimodalfeedbackachievescompactdistributionscenteredabove80%,high-
lightingrobustnessandreliability.
Overall,threefindingsemerge: (1)vision–languagefeedbacknotonlydetectsfailuresbutalsoguides
preciserepairs;(2)architecturalimprovementsinRoboTwin2.0accelerateconvergenceandreduce
tokenusage;and(3)combiningsymbolicexecutionlogswithperceptualdiagnosticsyieldsmore
reliable,semanticallyalignedexpertdata. Together,theseresultsvalidatetheeffectivenessofour
closed-loop,self-improvingcodegenerationarchitecture. Detailedsetups,metricdefinitions,and
additionalanalysesareprovidedinAppendixG.
4.2 EvaluatingEfficiencywithandwithoutAdaptiveGrasping
Table2: OverallPerformanceComparisonbetweenRoboTwin1.0andRoboTwin2.0.
Method Aloha-AgileX Piper Franka UR5 ARX-X5 Average
RoboTwin1.0 65.1% 2.4% 67.3% 57.6% 68.6% 52.2%
RoboTwin2.0 78.8% 25.1% 67.2% 57.1% 74.2% 60.5%
Difference +13.7% +22.7% -0.1% -0.5% +5.6% +8.3%
Toevaluatetheeffectivenessofourembodiment-awaregraspaugmentationstrategy,wemeasure
thetasksuccessrateofautomateddatacollectionacross50RoboTwin2.0tasksonfivedifferent
robot embodiments. As shown in Table 2, we compare our RoboTwin 2.0 pipeline against the
RoboTwin1.0baseline,whichlacksdiversegraspingandcandidateaugmentation. Resultsshow
thatourmethodimprovessuccessrates,particularlyforrobotswithconstrainedplanningspaces,
achievinganaverageimprovementof8.3%acrossallembodiments. Specifically,forhigh-DoFarms
withlargereachableworkspaces, suchasFrankaandUR5(7-DoF),successratesremainlargely
unchanged, indicating limited benefit when the robot already has sufficient kinematic flexibility.
However,forlower-DoFplatformssuchasAloha-AgileX,Piper,andARX-X5(6-DoF),ourmethod
8

--- Page 9 ---
leadstosubstantialgainsof13.5%,22.7%,and5.6%,respectively. Theseresultsdemonstratethatour
approachprovidesadditionalfeasiblegraspoptionsthateffectivelymitigatetheplanninglimitations
oflow-DoFmanipulators. SuccessratesforalltaskscanbefoundinAppendixL.
4.3 AssessingtheImpactofRoboTwin2.0onPolicyRobustness
Ourgoalistoevaluatewhetherthedomain-randomizeddatainRoboTwin2.0canendowmodels
withrobustnesstoenvironmentalperturbations. Tothisend,wefirstpre-trainRDTandPi0on9,600
experttrajectoriescollectedfrom32tasks(300pertask)undertwosettings: clean(non-randomized)
anddomain-randomized.
For comparison, we also evaluate the released pretrained weights of RDT and Pi0 without addi-
tionalfine-tuning. Tofurtherstudygeneralization,weselectfiveunseentasksandcollect50clean
demonstrationspertaskforsingle-tasktrainingandfine-tuning. Finally,allpolicies—includingACT,
DP,RDT,andPi0—areevaluatedunderdomain-randomizedconditionstomeasurerobustnessin
previouslyunseenenvironments. DetailedconfigurationsareprovidedinAppendixCandD.
Table3: EvaluatingtheImpactofRoboTwin2.0onPolicyRobustness.
Simulation ACT DP RDT Pi0 RDT Pi0 RDT Pi0
Tasks +Clean +Clean +Rand. +Rand.
StackBowlsTwo 0.0% 0.0% 30.0% 41.0% 8.0% 55.0% 49.0% 62.0%
PickDualBottles 0.0% 0.0% 13.0% 12.0% 12.0% 15.0% 17.0% 7.0%
MoveCanPot 4.0% 0.0% 12.0% 21.0% 13.0% 35.0% 18.0% 22.0%
PlaceObjectBasket 0.0% 0.0% 17.0% 2.0% 9.0% 8.0% 6.0% 22.0%
PlaceShoe 0.0% 0.0% 7.0% 6.0% 9.0% 6.0% 30.0% 18.0%
OpenLaptop 0.0% 0.0% 32.0% 46.0% 21.0% 33.0% 35.0% 50.0%
PressStapler 6.0% 0.0% 24.0% 29.0% 21.0% 26.0% 27.0% 31.0%
TurnSwitch 2.0% 1.0% 15.0% 23.0% 24.0% 21.0% 16.0% 21.0%
Average 2.0% 0.0% 18.8% 22.5% 14.6% 24.9% 24.8% 29.1%
AsshowninTable3,weobservethatmodelsfine-tunedwithcleandatashownegligibleimprovements
inaveragesuccessratecomparedtotheirpretrainedcounterparts,indicatingthatdatawithoutdomain
randomization does not help the model handle environmental variations. This also suggests that
thelowsuccessrateof pretrainedVLAsinsimulation isnotdueto aReal-to-Simgap, sincewe
providecleansimulationdatayetobservenoclearimprovement. Incontrast,modelspretrainedwith
RoboTwin2.0dataexhibitsignificantlyimprovedgeneralization. Specifically,RDTandPi0achieve
relativeimprovementsof31.9%and29.3%. Notably,thisperformancegainpersistseventhough
thedownstreamtasksweretrainedusingonlyclean,non-randomizeddata. Thisdemonstratesthat
domain-randomizedpretrainingwithRoboTwin2.0effectivelyequipsmodelswithrobustnessto
visualandspatialvariations. Asaresult,modelspretrainedwithRoboTwin2.0canadapttonew
taskswithoutrequiringadditionaldataaugmentationorcomplexscenevariations.
4.4 EvaluationonSim-to-RealPerformance
Seen Bg+ not Cluttered Unseen Bg+ not Cluttered Seen Bg+ Cluttered Unseen Bg+ Cluttered
Figure10: Real-WorldEvaluationacrossFourConfigurations.
9

--- Page 10 ---
ToevaluateRoboTwin2.0’seffectivenessinenhancingreal-worldpolicyrobustness,weconduct
experimentsonfourbimanualtasks: StackBowls,HandoverBlock,PickBottle,andClickBell. All
experiments use RDT as the policy backbone and are executed on the COBOT-Magic dual-arm
platform. Wecomparethreetrainingsettings: (1)10real-worlddemonstrationsincleantabletop
environments; (2)thesamedemonstrationsaugmentedwith1,000domain-randomizedsynthetic
trajectoriesgeneratedunderclutteredsceneswithvariedlightingandbackgrounds;and(3)asynthetic-
onlysettingtrainedsolelyonthe1,000domain-randomizedtrajectories.Tofurtherimproverobustness
tocamerajitterandcalibrationerrors,weapplyrandom3Dperturbationstosimulatedcameraposes
(positionandorientation),withthedisplacementmagnitudeboundedby1cm.
Evaluationisconductedunderfourtestconfigurations: (i)cleantabletopwithseenbackgrounds,
(ii)cleantabletopwithunseenbackgrounds,(iii)clutteredtabletopwithseenbackgrounds,and(iv)
clutteredtabletopwithunseenbackgrounds(Fig.10). Sincethesynthetic-onlysettingexcludesseen
backgroundsduringtraining,thecorrespondingentriesinTable4areomitted. Thissetupdirectly
testswhetherRoboTwin2.0enablesrobustpolicygeneralizationwithoutadditionalreal-worlddata
fromvisuallycomplexenvironments.
Table4: Real-WorldExperimentResults. Weconductcontrolledexperimentson4dual-armtasks:
StackBowls,HandoverBlock,PickBottle,andClickBell,eachevaluatedunder4differentsettings.
RealWorld Background Cluttered 10Clean 10CleanReal+ 1kRoboTwin2.0
Task Type orNot Real 1kRoboTwin2.0 (Zero-shot)
False 22.0% 64.0% /
Seen
True 12.0% 58.0% /
StackBowls
False 10.0% 50.0% 60.0%
Unseen
True 12.0% 56.0% 52.0%
False 40.0% 48.0% /
Seen
True 16.0% 12.0% /
HandoverBlock
False 36.0% 56.0% 56.0%
Unseen
True 0.0% 36.0% 20.0%
False 20.0% 36.0% /
Seen
True 8.0% 40.0% /
PickBottle
False 4.0% 26.0% 10.0%
Unseen
True 8.0% 28.0% 32.0%
False 36.0% 24.0% /
Seen
True 20.0% 56.0% /
ClickBell
False 12.0% 24.0% 20.0%
Unseen
True 16.0% 48.0% 14.0%
False 29.5% 43.0% /
Seen +13.5%
True 14.0% 41.5% /
Average +27.5%
False 15.5% 39.0% 36.5%
Unseen +23.5% +21.0%
True 9.0% 42.0% 29.5%
+33.0% +20.5%
The experimental results show that real-world bimanual policies augmented with RoboTwin 2.0
achievecleargainsinrobustness. Inthefew-shotsetting—where1,000domain-randomizedsynthetic
trajectoriesarecombinedwithjust10real-worlddemonstrations—theaveragesuccessrateacrossall
evaluationsettingsimprovesby24.4%,withper-configurationgainsof13.5%,27.5%,23.5%,and
33.0%,respectively. Inthezero-shotsettingtrainedsolelyonsyntheticdata,westillobservenotable
improvementsof21.0%and20.5%onthetwounseen-backgroundscenarios. Notably,performance
gainsbecomelargerinvisuallycomplexscenes,indicatingthatRoboTwin2.0isespeciallyeffective
underchallengingconditions.
Theseimprovementsstemfromtwofactors: (1)thehighvisualandphysicalfidelityofRoboTwin2.0,
enablingdirectsim-to-realtransfer,and(2)theabilityofdomain-randomizedsyntheticdatatoprepare
policiesforenvironmentalvariationsabsentfromcleanreal-worlddemonstrations. Importantly,the
10

--- Page 11 ---
strongperformanceofthefew-shotsettingsuggeststhatonlyminimalreal-worlddataisneededto
effectivelybridgethesim-to-realgap.
4.5 RoboTwin2.0Benchmark
To evaluate the benchmarking utility and generalization challenges of RoboTwin 2.0, we assess
fivepolicymodels: ACT,DP,RDT,Pi0,andDP3. AllVLAsarefine-tunedfromtheirreleased
pretrainedweightsinthesingle-tasksetting. Evaluationsareconductedonall50benchmarktasks
usingtheAlohaAgileXdual-armembodiment. Foreachtask, 50cleanexpertdemonstrations
areusedfortraining,andpoliciesaretestedwith100rolloutsundertwoconditions: Easy(clean)
andHard(domain-randomizedwithclutter,lighting,textures,andheightvariations). Weprovide
a visualization of the benchmark setting in Appendix J. We report success rates as indicators of
few-shotadaptationandrobustness. DetailedsetupsareprovidedinAppendixCandD,andfull
resultsareavailableinAppendixKandontheLeaderboard.
Table5: SubsetofRoboTwin2.0benchmark. FullresultsinAppendixKandLeaderboard.
SimulationTask RDT Pi0 ACT DP DP3
Easy Hard Easy Hard Easy Hard Easy Hard Easy Hard
AdjustBottle 81% 75% 90% 56% 97% 23% 97% 0% 99% 3%
BeatBlockHammer 77% 37% 43% 21% 56% 3% 42% 0% 72% 8%
BlocksRankingRGB 3% 0% 19% 5% 1% 0% 0% 0% 3% 0%
BlocksRankingSize 0% 0% 7% 1% 0% 0% 1% 0% 2% 0%
ClickAlarmclock 61% 12% 63% 11% 32% 4% 61% 5% 77% 14%
ClickBell 80% 9% 44% 3% 58% 3% 54% 0% 90% 0%
DumpBinBigbin 64% 32% 83% 24% 68% 1% 49% 0% 85% 53%
GrabRoller 74% 43% 96% 80% 94% 25% 98% 0% 98% 2%
HandoverBlock 45% 14% 45% 8% 42% 0% 10% 0% 70% 0%
HandoverMic 90% 31% 98% 13% 85% 0% 53% 0% 100% 3%
HangingMug 23% 16% 11% 3% 7% 0% 8% 0% 17% 1%
LiftPot 72% 9% 84% 36% 88% 0% 39% 0% 97% 0%
··· ···
MovePillbottlePad 8% 0% 21% 1% 0% 0% 1% 0% 41% 0%
Average(in%) 34.5 13.7 46.4 16.3 29.7 1.7 28.0 0.6 55.2 5.0
Fig.5 and Appendix K report results on 50 tasks. Non-pretrained models (ACT, DP, DP3) per-
formpoorlyunderHardconditions,whilepretrainedmodels(RDT,Pi0)showstrongerresilience,
suggestingthatvision–language–actionpretrainingprovidesusefulpriorsforgeneralization. Still,
successratesdropby20.8%(RDT)and30.1%(Pi0)fromcleantorandomizedsettings,underscoring
robustness under domain shifts as a key challenge, likely due to limited diversity in pretraining
data. DP3achievesthebestfew-shotperformancewithlimitedsamples,highlightingtheroleof3D
information,thoughitsstrongresultspartlystemfromperfectpointcloudsandcleanbackground
segmentationinsimulation. TogetherwithSections4.3and4.4,thesefindingsshowRoboTwin2.0’s
valueincomplementingexistingdatasetswithdiverse,domain-randomizedtrajectoriesforimproved
generalizationandrobustness.
5 RelatedWork
5.1 DatasetsandBenchmarksforRoboticManipulation
Physics-based simulators underpin modern manipulation research. Existing platforms provide
complementarystrengths: SAPIEN[48]enablesdynamicinteractionwith2,300+articulatedobjects;
ManiSkill2[16]suppliesmillionsofdemonstrations;Meta-World[50],CALVIN[32],LIBERO[30],
and RoboVerse [15] target multi-task, language-conditioned, lifelong, and domain-randomized
settings;RoboCasa[35]offerslarge-scalehumandemonstrationsbutlacksautomationanddual-arm
focus.
11

--- Page 12 ---
Large-scalereal-worlddatasetsfurtherbridgesim-to-real: AgiBotWorld[4],RoboMIND[47],Open
X-Embodiment[36],andBridge[12]contributemillionsoftrajectoriesacrossdiversetasks,robots,
andenvironments.
RoboTwin-1.0[34]mirroredrealdemonstrationswithsimulatedreplicasfordual-armbenchmarking.
Inthiswork,RoboTwin2.0integratesLLM-drivenfeedbackandsystematicdomainrandomization
acrossvisual,physical,andtaskdimensions,producingrichercorporathatimprovepolicyrobustness
andgeneralization. AdetailedcomparisonwithpriorbenchmarksisprovidedinAppendixB.
5.2 RobotLearninginManipulation
Manytask-specificpolicyarchitectures[42,21,51,9,14,7,29,42,27,28,45,44,8]achievestrong
single-taskperformancebutstruggletotransferacrossembodiments. Incontrast,foundationmodels
trainedonmillion-scale,multi-robotcorporahaveenabledrobustzero-shotgeneralization: RT-1[3]
unifies vision, language and actions in a single transformer for real-time kitchen tasks; RT-2 [2]
co-fine-tuneslargevision–languagemodelsonwebandrobotdatatounlocksemanticplanningand
objectreasoning;diffusion-basedRDT-1B[31]andtheπ [1]capturediversebimanualdynamics
0
from over a million episodes. Vision–language–action (VLA) frameworks like OpenVLA [23]
andCogACT[26],togetherwithadaptationslikeOcto[40],LAPA[49],andOpenVLA-OFT[22]
demonstrateefficientfine-tuningtonovelrobotsandsensormodalities.
To further advance this direction, our work introduces digital-twin data collection paired with
extensive domain randomization, yielding datasets that closely mirror real robot dynamics and
supportthetrainingofrobustandgeneralizablebi-manualmanipulationpolicies.
5.3 DomainRandomizationinImitationLearning
Priorworkshaveshownthatrandomizingvisualandphysicalparameters,includingbutnotlimited
totextures,lighting,camerapose,mass,frictionandcontrollatencycombinedwithnoiseinjection
in expert demonstrations, enables sim-to-real transfer and robust visuomotor policies [41, 37, 5,
7,28], andoptimizingoverworst-caseensemblesfurtherimprovesresiliencetoextremedomain
shifts[38,25,27]. However,theseapproachesapplyrandomizationinisolationandlackbidirectional
digital-twinfeedback;ourmethodintegratesinteractivesimulationfeedbackwithsystematicdomain
randomizationtogeneratehigher-fidelityimitationdata.
6 Conclusion
ThispaperpresentedRoboTwin2.0,ascalablesimulationframeworkforgeneratingdiverse,high-
fidelityexpertdatatosupportrobustbimanualmanipulation. OursystemintegratesMLLM-based
taskgeneration,embodiment-adaptivebehaviorsynthesis,andcomprehensivedomainrandomization
toaddresskeylimitationsinpriorsyntheticdatagenerator.
By leveraging an annotated object library and automating trajectory generation, RoboTwin 2.0
producesdatawithrichvisual,linguistic,andphysicaldiversitywhileminimizingmanualengineer-
ingeffort. Experimentsdemonstrateitseffectivenessinimprovingpolicyrobustnesstocluttered
environments,generalizationtounseentasks,andcross-embodimentmanipulation.
These findings highlight the importance of scalable, automated generation of semantically rich,
domain-randomizeddataforlearningrobustmanipulationpolicies. RoboTwin2.0providesafoun-
dation for unified benchmarks and scalable sim-to-real pipelines, with future work focusing on
real-worlddeploymentandmulti-objecttaskcomplexity.
7 Acknowledgments
ThispaperispartiallysupportedbyAgileXRobotics,D-Robotics,andtheJockeyClubSTEMLab
ofAutonomousIntelligentSystemsfundedbyTheHongKongJockeyClubCharitiesTrust.
12

--- Page 13 ---
References
[1] KevinBlack,NoahBrown,DannyDriess,AdnanEsmail,MichaelEqui,ChelseaFinn,NiccoloFusai,
LachyGroom,KarolHausman,BrianIchter,etal. pi_0:Avision-language-actionflowmodelforgeneral
robotcontrol. arXivpreprintarXiv:2410.24164,2024.
[2] AnthonyBrohan,NoahBrown,JusticeCarbajal,YevgenChebotar,XiChen,KrzysztofChoromanski,
TianliDing,DannyDriess,AvinavaDubey,ChelseaFinn,etal. Rt-2: Vision-language-actionmodels
transferwebknowledgetoroboticcontrol. arXivpreprintarXiv:2307.15818,2023.
[3] AnthonyBrohan,NoahBrown,JusticeCarbajal,YevgenChebotar,JosephDabis,ChelseaFinn,Keerthana
Gopalakrishnan, Karol Hausman, Alex Herzog, Jasmine Hsu, et al. Rt-1: Robotics transformer for
real-worldcontrolatscale. arXivpreprintarXiv:2212.06817,2022.
[4] Qingwen Bu, Jisong Cai, Li Chen, Xiuqi Cui, Yan Ding, Siyuan Feng, Shenyuan Gao, Xindong He,
XuHuang,ShuJiang,etal. Agibotworldcolosseo:Alarge-scalemanipulationplatformforscalableand
intelligentembodiedsystems. arXivpreprintarXiv:2503.06669,2025.
[5] YevgenChebotar,AnkurHanda,ViktorMakoviychuk,MilesMacklin,JanIssac,NathanRatliff,andDieter
Fox. Closingthesim-to-realloop:Adaptingsimulationrandomizationwithrealworldexperience. In2019
InternationalConferenceonRoboticsandAutomation(ICRA),pages8973–8979.IEEE,2019.
[6] JuntingChen,YaoMu,QiaojunYu,TianmingWei,SilangWu,ZhechengYuan,ZhixuanLiang,Chao
Yang,KaipengZhang,WenqiShao,YuQiao,HuazheXu,MingyuDing,andPingLuo. Roboscript:Code
generationforfree-formmanipulationtasksacrossrealandsimulation,2024.
[7] TianxingChen,YaoMu,ZhixuanLiang,ZanxinChen,ShijiaPeng,QiangyuChen,MingkunXu,Ruizhen
Hu, Hongyuan Zhang, Xuelong Li, et al. G3flow: Generative 3d semantic flow for pose-aware and
generalizable object manipulation. In Proceedings of the Computer Vision and Pattern Recognition
Conference,pages1735–1744,2025.
[8] TianxingChen,KaixuanWang,ZhaohuiYang,YuhaoZhang,ZanxinChen,BaijunChen,WanxiDong,
Ziyuan Liu, Dong Chen, Tianshuo Yang, et al. Benchmarking generalizable bimanual manipulation:
Robotwindual-armcollaborationchallengeatcvpr2025meisworkshop.arXivpreprintarXiv:2506.23351,
2025.
[9] ChengChi,ZhenjiaXu,SiyuanFeng,EricCousineau,YilunDu,BenjaminBurchfiel,RussTedrake,and
ShuranSong. Diffusionpolicy:Visuomotorpolicylearningviaactiondiffusion. TheInternationalJournal
ofRoboticsResearch,page02783649241273668,2023.
[10] MattDeitke,DustinSchwenk,JordiSalvador,LucaWeihs,OscarMichel,EliVanderBilt,LudwigSchmidt,
KianaEhsani,AniruddhaKembhavi,andAliFarhadi. Objaverse:Auniverseofannotated3dobjects. In
ProceedingsoftheIEEE/CVFconferenceoncomputervisionandpatternrecognition,pages13142–13153,
2023.
[11] ShengliangDeng,MiYan,SonglinWei,HaixinMa,YuxinYang,JiayiChen,ZhiqiZhang,TaoyuYang,
XuhengZhang,HemingCui,etal. Graspvla: agraspingfoundationmodelpre-trainedonbillion-scale
syntheticactiondata. arXivpreprintarXiv:2505.03233,2025.
[12] FrederikEbert,YanlaiYang,KarlSchmeckpeper,BernadetteBucher,GeorgiosGeorgakis,KostasDani-
ilidis, Chelsea Finn, and Sergey Levine. Bridge data: Boosting generalization of robotic skills with
cross-domaindatasets. arXivpreprintarXiv:2109.13396,2021.
[13] ZhangyinFeng,DayaGuo,DuyuTang,NanDuan,XiaochengFeng,MingGong,LinjunShou,BingQin,
TingLiu,DaxinJiang,etal. Codebert:Apre-trainedmodelforprogrammingandnaturallanguages. arXiv
preprintarXiv:2002.08155,2020.
[14] ZipengFu,TonyZZhao,andChelseaFinn. Mobilealoha:Learningbimanualmobilemanipulationwith
low-costwhole-bodyteleoperation. arXivpreprintarXiv:2401.02117,2024.
[15] HaoranGeng,FeishiWang,SonglinWei,YuyangLi,BangjunWang,BoshiAn,CharlieTianyueCheng,
Haozhe Lou, Peihao Li, Yen-Jen Wang, et al. Roboverse: Towards a unified platform, dataset and
benchmarkforscalableandgeneralizablerobotlearning. arXivpreprintarXiv:2504.18904,2025.
[16] JiayuanGu,FanboXiang,XuanlinLi,ZhanLing,XiqiangLiu,TongzhouMu,YiheTang,StoneTao,
XinyueWei,YunchaoYao,etal. Maniskill2:Aunifiedbenchmarkforgeneralizablemanipulationskills.
InTheEleventhInternationalConferenceonLearningRepresentations,2023.
13

--- Page 14 ---
[17] DayaGuo,ShuaiLu,NanDuan,YanlinWang,MingZhou,andJianYin. Unixcoder:Unifiedcross-modal
pre-trainingforcoderepresentation. arXivpreprintarXiv:2203.03850,2022.
[18] MengkangHu,TianxingChen,QiguangChen,YaoMu,WenqiShao,andPingLuo. Hiagent:Hierarchical
workingmemorymanagementforsolvinglong-horizonagenttaskswithlargelanguagemodel. arXiv
preprintarXiv:2408.09559,2024.
[19] MengkangHu,TianxingChen,YudeZou,YuhengLei,QiguangChen,MingLi,YaoMu,Hongyuan
Zhang,WenqiShao,andPingLuo. Text2world:Benchmarkinglargelanguagemodelsforsymbolicworld
modelgeneration. arXivpreprintarXiv:2502.13092,2025.
[20] PuHua,MinghuanLiu,AnnabellaMacaluso,YunfengLin,WeinanZhang,HuazheXu,andLiruiWang.
Gensim2:Scalingrobotdatagenerationwithmulti-modalandreasoningllms. In8thAnnualConference
onRobotLearning.
[21] Tsung-WeiKe,NikolaosGkanatsios,andKaterinaFragkiadaki. 3ddiffuseractor:Policydiffusionwith3d
scenerepresentations. arXivpreprintarXiv:2402.10885,2024.
[22] MooJinKim,ChelseaFinn,andPercyLiang. Fine-tuningvision-language-actionmodels:Optimizing
speedandsuccess. arXivpreprintarXiv:2502.19645,2025.
[23] MooJinKim,KarlPertsch,SiddharthKaramcheti,TedXiao,AshwinBalakrishna,SurajNair,Rafael
Rafailov,EthanPFoster,PannagRSanketi,QuanVuong,etal. Openvla:Anopen-sourcevision-language-
actionmodel. In8thAnnualConferenceonRobotLearning.
[24] Zhiqian Lan, Yuxuan Jiang, Ruiqi Wang, Xuanbing Xie, Rongkui Zhang, Yicheng Zhu, Peihang Li,
TianshuoYang,TianxingChen,HaoyuGao,etal. Autobio: Asimulationandbenchmarkforrobotic
automationindigitalbiologylaboratory. arXivpreprintarXiv:2505.14030,2025.
[25] MichaelLaskey,JonathanLee,RoyFox,AncaDragan,andKenGoldberg.Dart:Noiseinjectionforrobust
imitationlearning. InConferenceonrobotlearning,pages143–156.PMLR,2017.
[26] QixiuLi,YaoboLiang,ZeyuWang,LinLuo,XiChen,MozhengLiao,FangyunWei,YuDeng,Sicheng
Xu,YizhongZhang,etal. Cogact:Afoundationalvision-language-actionmodelforsynergizingcognition
andactioninroboticmanipulation. arXivpreprintarXiv:2411.19650,2024.
[27] Zhixuan Liang, Yao Mu, Mingyu Ding, Fei Ni, Masayoshi Tomizuka, and Ping Luo. Adaptdiffuser:
Diffusionmodelsasadaptiveself-evolvingplanners. InInternationalConferenceonMachineLearning,
pages20725–20745.PMLR,2023.
[28] ZhixuanLiang,YaoMu,HengboMa,MasayoshiTomizuka,MingyuDing,andPingLuo. Skilldiffuser:
Interpretablehierarchicalplanningviaskillabstractionsindiffusion-basedtaskexecution. InProceedings
oftheIEEE/CVFConferenceonComputerVisionandPatternRecognition,pages16467–16476,2024.
[29] ZhixuanLiang,YaoMu,YixiaoWang,TianxingChen,WenqiShao,WeiZhan,MasayoshiTomizuka,
PingLuo,andMingyuDing. Dexhanddiff:Interaction-awarediffusionplanningforadaptivedexterous
manipulation. InProceedingsoftheComputerVisionandPatternRecognitionConference,pages1745–
1755,2025.
[30] Bo Liu, Yifeng Zhu, Chongkai Gao, Yihao Feng, Qiang Liu, Yuke Zhu, and Peter Stone. Libero:
Benchmarkingknowledgetransferforlifelongrobotlearning. AdvancesinNeuralInformationProcessing
Systems,36:44776–44791,2023.
[31] SongmingLiu,LingxuanWu,BangguoLi,HengkaiTan,HuayuChen,ZhengyiWang,KeXu,Hang
Su, and Jun Zhu. Rdt-1b: a diffusion foundation model for bimanual manipulation. arXiv preprint
arXiv:2410.07864,2024.
[32] OierMees,LukasHermann,ErickRosete-Beas,andWolframBurgard.Calvin:Abenchmarkforlanguage-
conditionedpolicylearningforlong-horizonrobotmanipulationtasks. IEEERoboticsandAutomation
Letters,7(3):7327–7334,2022.
[33] Yao Mu, Junting Chen, Qing-Long Zhang, Shoufa Chen, Qiaojun Yu, Chongjian Ge, Runjian Chen,
ZhixuanLiang,MengkangHu,ChaofanTao,etal. Robocodex:Multimodalcodegenerationforrobotic
behaviorsynthesis. InInternationalConferenceonMachineLearning,pages36434–36454.PMLR,2024.
[34] YaoMu,TianxingChen,ZanxinChen,ShijiaPeng,ZhiqianLan,ZeyuGao,ZhixuanLiang,Qiaojun
Yu,YudeZou,MingkunXu,etal. Robotwin:Dual-armrobotbenchmarkwithgenerativedigitaltwins.
ProceedingsoftheIEEE/CVFconferenceoncomputervisionandpatternrecognition,2025.
14

--- Page 15 ---
[35] SoroushNasiriany,AbhiramMaddukuri,LanceZhang,AdeetParikh,AaronLo,AbhishekJoshi,Ajay
Mandlekar,andYukeZhu. Robocasa:Large-scalesimulationofeverydaytasksforgeneralistrobots. In
Robotics:ScienceandSystems(RSS),2024.
[36] AbbyO’Neill,AbdulRehman,AbhiramMaddukuri,AbhishekGupta,AbhishekPadalkar,AbrahamLee,
AcornPooley,AgrimGupta,AjayMandlekar,AjinkyaJain,etal. Openx-embodiment:Roboticlearning
datasetsandrt-xmodels:Openx-embodimentcollaboration0. In2024IEEEInternationalConferenceon
RoboticsandAutomation(ICRA),pages6892–6903.IEEE,2024.
[37] XueBinPeng,MarcinAndrychowicz,WojciechZaremba,andPieterAbbeel. Sim-to-realtransferof
roboticcontrolwithdynamicsrandomization. In2018IEEEinternationalconferenceonroboticsand
automation(ICRA),pages3803–3810.IEEE,2018.
[38] AravindRajeswaran,SarvjeetGhotra,BalaramanRavindran,andSergeyLevine. Epopt:Learningrobust
neuralnetworkpoliciesusingmodelensembles. InInternationalConferenceonLearningRepresentations,
2017.
[39] Shuo Ren, Daya Guo, Shuai Lu, Long Zhou, Shujie Liu, Duyu Tang, Neel Sundaresan, Ming Zhou,
AmbrosioBlanco,andShuaiMa. Codebleu:amethodforautomaticevaluationofcodesynthesis. arXiv
preprintarXiv:2009.10297,2020.
[40] OctoModelTeam,DibyaGhosh,HomerWalke,KarlPertsch,KevinBlack,OierMees,SudeepDasari,
JoeyHejna,TobiasKreiman,CharlesXu,etal. Octo: Anopen-sourcegeneralistrobotpolicy. arXiv
preprintarXiv:2405.12213,2024.
[41] JoshTobin,RachelFong,AlexRay,JonasSchneider,WojciechZaremba,andPieterAbbeel. Domain
randomizationfortransferringdeepneuralnetworksfromsimulationtotherealworld. In2017IEEE/RSJ
internationalconferenceonintelligentrobotsandsystems(IROS),pages23–30.IEEE,2017.
[42] ChenxiWang,HongjieFang,Hao-ShuFang,andCewuLu. Rise:3dperceptionmakesreal-worldrobot
imitationsimpleandeffective. In2024IEEE/RSJInternationalConferenceonIntelligentRobotsand
Systems(IROS),pages2870–2877.IEEE,2024.
[43] Yufei Wang, Zhou Xian, Feng Chen, Tsun-Hsuan Wang, Yian Wang, Katerina Fragkiadaki, Zackory
Erickson,DavidHeld,andChuangGan. Robogen:Towardsunleashinginfinitedataforautomatedrobot
learningviagenerativesimulation,2023.
[44] JunjieWen, YichenZhu, JinmingLi, ZhibinTang, ChaominShen, andFeifeiFeng. Dexvla: Vision-
languagemodelwithplug-indiffusionexpertforgeneralrobotcontrol. arXivpreprintarXiv:2502.05855,
2025.
[45] JunjieWen,YichenZhu,JinmingLi,MinjieZhu,ZhibinTang,KunWu,ZhiyuanXu,NingLiu,Ran
Cheng,ChaominShen,YaxinPeng,FeifeiFeng,andJianTang. Tinyvla:Towardfast,data-efficientvision-
language-actionmodelsforroboticmanipulation.IEEERoboticsandAutomationLetters,10(4):3988–3995,
2025.
[46] WuWen,XiaoboXue,YaLi,PengGu,andJianfengXu. Codesimilaritydetectionusingastandtextual
information. InternationalJournalofPerformabilityEngineering,15(10):2683,2019.
[47] KunWu,ChengkaiHou,JiamingLiu,ZhengpingChe,XiaozhuJu,ZhuqinYang,MengLi,YinuoZhao,
ZhiyuanXu,GuangYang,etal. Robomind:Benchmarkonmulti-embodimentintelligencenormativedata
forrobotmanipulation. arXivpreprintarXiv:2412.13877,2024.
[48] FanboXiang,YuzheQin,KaichunMo,YikuanXia,HaoZhu,FangchenLiu,MinghuaLiu,HanxiaoJiang,
YifuYuan,HeWang,etal. Sapien:Asimulatedpart-basedinteractiveenvironment. InProceedingsofthe
IEEE/CVFconferenceoncomputervisionandpatternrecognition,pages11097–11107,2020.
[49] SeonghyeonYe,JoelJang,ByeonggukJeon,SeJuneJoo,JianweiYang,BaolinPeng,AjayMandlekar,
ReubenTan,Yu-WeiChao,BillYuchenLin,etal. Latentactionpretrainingfromvideos. InCoRL2024
WorkshoponWhole-bodyControlandBimanualManipulation:ApplicationsinHumanoidsandBeyond.
[50] TianheYu,DeirdreQuillen,ZhanpengHe,RyanJulian,KarolHausman,ChelseaFinn,andSergeyLevine.
Meta-world:Abenchmarkandevaluationformulti-taskandmetareinforcementlearning. InConference
onrobotlearning,pages1094–1100.PMLR,2020.
[51] YanjieZe,GuZhang,KangningZhang,ChenyuanHu,MuhanWang,andHuazheXu. 3ddiffusionpolicy.
arXive-prints,pagesarXiv–2403,2024.
[52] YukeZhu,JosiahWong,AjayMandlekar,RobertoMartín-Martín,AbhishekJoshi,SoroushNasiriany,and
YifengZhu. robosuite:Amodularsimulationframeworkandbenchmarkforrobotlearning. arXivpreprint
arXiv:2009.12293,2020.
15

--- Page 16 ---
A Contributions
ProjectLeaders RoboTwin-OD
TianxingChen,YaoMu,ZhixuanLiang BaijunChen, QiangyuChen, KailunSu, Xuan-
bingXie,ZanxinChen
Roadmap&Methodology
Yao Mu, Tianxing Chen, Ping Luo, Yusen Qin, PoliciesTraining&Evaluation
XiaokangYang,KaixuanWang TianxingChen,ZijianCai,TianNian,Huan-ang
Gao,TianlingXu
DataGenerator&Benchmark
TianxingChen,ZanxinChen,BaijunChen,Qi- Real-WorldDeployment
weiLiang,ZixuanLi,XianliangLin TianxingChen,TianNian,WeiliangDeng
CodeGenAgent DomainRandomization
Yibin Liu, Zanxin Chen, Yiheng Ge, Tianxing BaijunChen,YubinGuo,QiweiLiang,Zhenyu
Chen,MengkangHu Gu,GuodongLiu,ZanxinChen,TianxingChen
B BenchmarkingRoboTwin2.0AgainstExistingDatasets
WecompareRoboTwin2.0againstexistingbenchmarksanddatasetsacrossseveralkeydimensions,
includingthenumberofsupportedtasks,thepresenceofdomainrandomization,supportforautomatic
datageneration,andcompatibilitywithvision-language-action(VLA)modeltrainingandevaluation.
ThecomparisonissummarizedinTable6.
Table6: ComparisonofRoboTwin2.0withpreviousmanipulationbenchmarksanddatasets.
Domain AutoData VLAModel
Benchmark&Dataset #Tasks
Randomization Generation Train&Eval
Meta-world[50] 50 ✕ ✓ ✕
Robosuite[52] 9 ✕ ✕ ✕
RoboCasa[50] 25 ✓ ✕ ✕
Maniskill2[16] 20 ✕ ✓ ✕
AutoBio[24] 16 ✕ ✓ ✓
RoboTwin1.0[34] 14 ✕ ✓ ✓
RoboTwin2.0(ours) 50 ✓ ✓ ✓
C DomainRandomizationSetting
Domainrandomizationinallexperimentsincludesclutteredscenes,randomlighting,tableheight
variation(upto3cm),unseenlanguageinstructionsandrandomizedbackgroundtextures.
D PoliciesTrainingDetails
RDTinexperiment4.3waspretrainedfor100,000stepswithabatchsizeof16perGPUon8GPUs,
andallsingle-taskfine-tuningwasconductedfor10,000stepswithabatchsizeof16perGPUon4
GPUs.
Pi0inexperiment4.3waspretrainedfor100,000stepswithabatchsizeof32,andallfine-tuning
wasperformedfor30,000stepsusingthesamebatchsize.
ACTwastrainedunderaunifiedsetupwithachunksizeof50, batchsizeof8, andsingle-GPU
trainingfor6,000epochs. Duringdeployment,weappliedtemporal_aggfortemporalaggregation
toimproveexecutionstability.
DPwastrainedfor600epochswithabatchsizeof128andaplanninghorizonof8.
DP3wastrainedfor3,000epochswithabatchsizeof256,usingaplanninghorizonof8andapoint
cloudresolutionof1,024,withprecisesegmentationofthebackgroundandtabletop.
16

--- Page 17 ---
E SupportforFlexibleEmbodimentCombinations
Ourobject-centric,embodiment-agnosticdatagenerationframeworkenablesseamlessdeployment
acrossawiderangeofdual-armroboticsystems. Thepipelinesupportsflexibleembodimentconfigu-
rations,allowingarbitrarycombinationsofheterogeneousmanipulatorsandrelativearmplacements.
Thisdesignensurescompatibilitywithdiversehardwaresetupsandfacilitatesextensibilitytofuture
roboticplatforms.
Figure11: HeterogeneousDual-ArmControlviaObject-CentricManipulation.
Toexecutehigh-success-ratemanipulationtrajectoriesacrossdifferentembodiments(seeSection2.3),
weintegrateCurobo,ahigh-performance,GPU-acceleratedmotionplannerthatenablesefficientand
reliableplanningundervariedkinematicconstraints.
Currently,ourframeworksupportsfiveroboticarms—Franka,Piper,UR5,ARX-X5,andAloha-
AgileX—along with multiple gripper types, including the Panda gripper and WSG gripper. As
showninFig.11,wedemonstratesuccessfultaskexecutionsacrossavarietyofdual-armpairings,
highlightingRoboTwin2.0’sabilitytoscaletoheterogeneousrobotconfigurationsanditsreadiness
forfuturereal-worlddeployment.
F ImprovementsofRoboTwin2.0overRoboTwin1.0PolicyCodebase
Metric RoboTwin1.0 RoboTwin2.0
PromptTokenLength↓ 5901.0 4719.1
CodeTokenLength↓ 1236.6 569.4
ParallelismControl↑ ✗ ✓
ASTSimilarity[46]↑ 23.72% 44.78%
CodeBLEUSimilarity[39]↑ 17.18% 18.53%
CodeBERTSimilarity[13]↑ 97.72% 98.80%
UnixcoderSimilarity[17]↑ 76.24% 82.21%
Avg. VLMTokenCost(perobservation) – 6894
Table7:CodeGenerationEfficiencyandQualityComparison.Evaluationofpromptandgenerated
code characteristics, along with code similarity metrics (AST Structural Similarity, CodeBERT,
Unixcodercosinesimilarity)againstexpert-writtencode,forRoboTwin1.0andRoboTwin2.0in
zero-shotgeneration. TheVLMobservercostisalsoreportedforRoboTwin2.0.
WefirstquantifythearchitecturalimpactofRoboTwin2.0inaone-shotgenerationwithoutcode
repairanditerativerefinement.Table7showsthatRoboTwin2.0yieldssignificantlyshorterprograms
(569.4vs.1236.6tokens), withreducedpromptlengthandhigherstructuralsimilaritytohuman-
writtencode. Crucially,itenablesdual-armparallelismviaaunifiedAPIabstraction,whichisabsent
inRoboTwin1.0.
TheseimprovementsstemfromthestructuredpromptingandgeometricAPImodularizationdesigned
intoRoboTwin2.0. HigherASTsimilarity(+21.06%),CodeBERTsimilarity(+1.08%),andUnix-
coderalignment(+5.97%)indicatethatRoboTwin2.0notonlyreducescodesizebutalsoimproves
semanticclarityandfunctionalalignment.
Inaddition,RoboTwin2.0integratesaVLMobserver,aplug-and-playmoduletriggeredonlywhen
executionfails. Toquantifyitsoverhead,weestimatedVLMusageviatheKimiAPI(assumingeach
image=1,024tokens)overthreerepresentativetasks: theaveragecostwas6,295inputtokensand
599outputtokens,totaling6,894tokens. Whilethisintroducesmoderateoverhead,theVLMenables
17

--- Page 18 ---
RoboTwin 2.0 to catch and correct errors invisible to execution logging, significantly enhancing
robustnessandoveralltasksuccess. Importantly,theobserverremainsoptionalandcanbedisabled
whenprioritizingtokenefficiency.
G ExperimentalDetailsandMetricDefinitionsforCodeGeneration
We use the DeepSeek-V3 model for program synthesis and the moonshot-v1-32k-vision-preview
modelformultimodalerrorlocalizationandverification. Thesemodelswereselectedfortheirstrong
performanceinlanguagereasoningandvisualunderstandingwhilemaintainingefficiencysuitable
for large-scale iterative refinement. The success rate of the i-th program is computed as R =
i
1 (cid:80)M s ,andthefinalsuccessrateforagiventaskunderaspecificsystemvariantisthendefined
M j=1 i,j
asR = 1 (cid:80)N R . Fordetailedusageinstructions,refertohttps://robotwin-platform.
task N i=1 i
github.io/doc/usage/expert-code-gen.html.
G.1 MetricDefinitions
Wereportthefollowingmetricsacrossalltasks:
ASR(AverageSuccessRate)istheaverageofR_taskacrossall10tasks. Itreflectsoveralltask
performanceacrossallgeneratedprograms.
Top5-ASRisthemeansuccessratecomputedusingonlythetop5highest-performingprogramsper
task. Thismetricestimatessystempotentialunderabest-of-selectionstrategy.
CR-Iter indicates the average number of feedback iterations required per task before reaching a
successrateabove50%orexhaustingtheiterationbudget.
Tokendenotestheaveragenumberoftokensofpolicycodegeneratedbythelanguagemodelper
task. ItservesasaproxyforcomputationalcostandLLMinferencebudget.
Thesemetricsjointlyevaluateboththereliabilityandefficiencyoftheexpertdatagenerationpipeline
undervaryingconditionsoffeedback,modelcapability,andrefinementstrategy.
G.2 Task-SpecificPerformanceComparisononCodeGeneration
WecomparethecodegenerationsuccessratesofRoboTwin2.0andRoboTwin1.0acrossalltasks.
Asshown,RoboTwin2.0consistentlymatchesoroutperformsthebaselineonthemajorityoftasks,
demonstratingtheeffectivenessofourmultimodalfeedbackandrefinementpipeline.
Task R1.0Vanilla R1.0+FB R1.0+MMFB R2.0Vanilla R2.0+FB R2.0+MMFB
beat_block_hammer 16% 48% 56% 23% 34% 53%
handover_block 2% 41% 45% 17% 50% 27%
pick_diverse_bottles 65% 65% 64% 60% 60% 62%
pick_dual_bottles 99% 99% 100% 100% 100% 100%
place_container_plate 66% 79% 91% 84% 84% 82%
place_dual_shoes 19% 22% 25% 0% 2% 22%
place_empty_cup 90% 90% 100% 61% 61% 85%
place_shoe 72% 90% 90% 100% 100% 100%
stack_blocks_three 1% 2% 4% 76% 76% 82%
stack_blocks_two 44% 68% 64% 100% 100% 100%
Table 8: Task-Specific Performance Comparison between RoboTwin 2.0 and RoboTwin 1.0.
R1.0/R2.0: RoboTwin1.0/2.0. Boldnumbersindicatethebestresultforeachtask.
G.3 Per-taskSuccessRatesofCodeGeneration
WereportthesuccessratesofalltasksinTab.9.
18

--- Page 19 ---
Table 9: Per-task success rates of our proposed R2.0 + MM FB algorithm on all RoboTwin
2.0-supportedtasks.
Task Rate Task Rate Task Rate Task Rate
AdjustBottle 100% BeatBlockHammer 53% BlocksRankingRgb 80% BlocksRankingSize 80%
ClickAlarmclock 0% ClickBell 10% DumpBinBigbin 0% GrabRoller 74%
HandoverBlock 27% HandoverMic 0% HangingMug 0% LiftPot 40%
MoveCanPot 30% MovePillbottlePad 50% MovePlayingcardAway 90% MoveStaplerPad 100%
OpenLaptop 0% OpenMicrowave 0% PickDiverseBottles 62% PickDualBottles 100%
PlaceA2BLeft 50% PlaceA2BRight 60% PlaceBreadBasket 0% PlaceBreadSkillet 0%
PlaceCanBasket 0% PlaceCansPlasticbox 100% PlaceContainerPlate 82% PlaceDualShoes 22%
PlaceEmptyCup 85% PlaceFan 70% PlaceBurgerFries 100% PlaceMousePad 100%
PlaceObjectBasket 0% PlaceObjectScale 80% PlaceObjectStand 90% PlacePhoneStand 0%
PlaceShoe 100% PressStapler 0% PutBottlesDustbin 0% PutObjectCabinet 0%
RotateQrcode 80% ScanObject 0% ShakeBottle 0% ShakeBottleHorizontally 0%
StackBlocksThree 82% StackBlocksTwo 100% StackBowlsThree 20% StackBowlsTwo 30%
StampSeal 20% TurnSwitch 0% AvgSuccessRate 43.34%
G.4 MultimodalObservationandErrorLocalization
To further investigate the capability of the VLM observer, we manually curated a dataset of 130
executionsequences,including101failedtrialsand29successfultrials. Eachsequenceconsistsof
thenaturallanguagetaskinstruction,aseriesofvisualobservations,andpolicycode. Thisdataset
enablesustoevaluatebothbinaryerrordetectionandfine-grainederrorlocalization.
ErrorDetection. TheVLMobserverwasfirsttaskedwithevaluatingwhetheraroboticexecution
successfullycompletedtheinstructedtask. Theconfusionmatrixisasfollows: TP=16,FP=61,TN
=40,FN=13. Thederivedperformancemetricsare: Accuracy=0.431,Precision=0.208,Recall
=0.552,andF1-score=0.302. TheseresultssuggestthatwhiletheVLMobserverisreasonably
sensitiveinidentifyingexecutionfailures(recall),itstendencytoover-predicterrorsleadstoahigh
falsepositiverate.
Error Localization. For failed executions, we further tested whether the VLM observer could
correctlylocalizetheprogramsteporcodesnippetthatledtofailure. Amongthe40truenegative
samples(correctlyidentifiedfailedtrials),theobserversuccessfullypinpointedthefailurestepin12
cases,yieldingalocalizationaccuracyof30%.Thisindicatesthat,whiletheobservershowspromising
diagnosticability,thereremainssignificantroomforimprovementinreliableerrorattribution.
CaseStudy. WeillustrateonesuccessfulcaseofVLMobserverreasoning. Givenataskinstruction
andfivevisualobservations,theobserverproducedastep-by-stepanalysis:
Step1: Theleftarmsuccessfullypicksupthemugfromtheleftside.
Step2: Theleftarmsuccessfullyplacesthemugatthemiddleposition.
Step3: Therightarmsuccessfullypicksupthemugfromthemiddleposition.
Step4: Therightarmattemptstohangthemugontherackbutfails.
Step5: Therightarmisintheprocessofmovingawayafterattemptingtohang
themug.
Theoveralltaskwasnotsuccessfullycompleted. ThefailureoccurredinStep4,
wheretherightarmattemptedtohangthemugontherackbutdidnotsucceed.
Themugisnotproperlypositionedontherack. Theerrormessageinthecode
indicatesanAttributeError: ’list’objecthasnoattribute’p’. Thiserroroccursin
the line where the target_point is being set to middle_target_pose.p. The issue
islikelyduetothefactthatmiddle_target_poseisalist,andlistsdonothavean
attribute’p’. Thecodeshouldbemodifiedtocorrectlyaccessthepositiondata
fromthemiddle_target_poselist.
Tofixtheerror,thecodeshouldbeupdatedtoaccessthepositiondatacorrectly.
Forexample,ifmiddle_target_poseisalistcontainingthepositionandorientation,
thepositiondatashouldbeaccessedusingmiddle_target_pose[0]insteadofmid-
dle_target_pose.p. Additionally,thefailureinStep4couldbeduetotheincorrect
positionororientationofthemugwhenattemptingtohangitontherack. The
codeshouldbereviewedtoensurethatthemugispositionedandorientedcorrectly
beforeexecutingthehangingmotion.
19

--- Page 20 ---
FailureModes. Despitethesesuccesses,wealsoobservedcaseswheretheVLMobserverfails.
Misclassificationsprimarilyoccurinfailedexecutions:theobservermayhallucinatecorrectoutcomes
oroverlooksubtleorientationerrors. Forinstance,inastackingtaskwhereboxesaremisaligned,the
observersometimesmarkstheexecutionassuccessfulifallboxesareplacedontopofeachother.
Similarly,intasksrequiringfine-grainedposeaccuracy(e.g.,placingshoesinthecorrectorientation),
smallbutcriticalerrorsmaybeignored. Furthermore,failuresstemmingfrominvisiblefactors—such
asincorrectgraspaxisparameters—remainchallengingforpurelyvision-basedobserverstodiagnose.
G.5 LLM-GeneratedCodeandHuman-WrittenCodeCaseStudy
LLM-GeneratedCode(gpt_place_shoe)
class gpt_place_shoe(place_shoe):
def play_once(self):
# Initial observation
self.save_camera_images(task_name="place_shoe", step_name="
step1_initial_scene_state", generate_num_id="generate_num_0")
# Get the shoe’s position to determine which arm to use
shoe_pose = self.shoe.get_pose()
shoe_position = shoe_pose.p
arm_tag = ArmTag("left" if shoe_position[0] < 0 else "right")
# Grasp the shoe
self.move(self.grasp_actor(actor=self.shoe, arm_tag=arm_tag, pre_grasp_dis
=0.1, grasp_dis=0))
self.save_camera_images(task_name="place_shoe", step_name="
step2_shoe_grasped", generate_num_id="generate_num_0")
# Lift the shoe up to avoid collision
self.move(self.move_by_displacement(arm_tag=arm_tag, z=0.07, move_axis=’
world’))
self.save_camera_images(task_name="place_shoe", step_name="step3_shoe_lifted
", generate_num_id="generate_num_0")
# Get target pose from the top functional point of the target block
target_pose = self.target_block.get_functional_point(1, "pose")
# Place the shoe on the target block with head towards left side
self.move(self.place_actor(actor=self.shoe, arm_tag=arm_tag, target_pose=
target_pose, functional_point_id=0, pre_dis=0.1, dis=0.02, is_open=True,
constrain="align", pre_dis_axis=’fp’))
self.save_camera_images(task_name="place_shoe", step_name="step4_shoe_placed
", generate_num_id="generate_num_0")
# Lift the gripper up after placing
self.move(self.move_by_displacement(arm_tag=arm_tag, z=0.07, move_axis=’
world’))
# Return arm to origin
self.move(self.back_to_origin(arm_tag=arm_tag))
# Final observation
self.move(self.save_camera_images(task_name="place_shoe", step_name="
step5_final_scene_state", generate_num_id="generate_num_0"))
Listing1: LLM-GeneratedCodeforgpt_place_shoeTask
Human-WrittenCode(place_shoe)
class place_shoe(base_task):
def play_once(self):
# Get the shoe’s position to determine which arm to use
shoe_pose = self.shoe.get_pose().p
20

--- Page 21 ---
arm_tag = ArmTag("left" if shoe_pose[0] < 0 else "right")
# Grasp the shoe with specified pre-grasp distance and gripper position
self.move(self.grasp_actor(self.shoe, arm_tag=arm_tag, pre_grasp_dis=0.1,
gripper_pos=0))
# Lift the shoe up by 0.07 meters in z-direction
self.move(self.move_by_displacement(arm_tag=arm_tag, z=0.07))
# Get target_block’s functional point as target pose
target_pose = self.target_block.get_functional_point(0)
# Place the shoe on the target_block with alignment constraint and specified
pre-placement distance
self.move(self.place_actor(self.shoe, arm_tag=arm_tag, target_pose=
target_pose, functional_point_id=0, pre_dis=0.12, constrain="align"))
# Open the gripper to release the shoe
self.move(self.open_gripper(arm_tag=arm_tag))
Listing2: Human-WrittenCodeforplace_shoeTask
TheLLMgeneratedcodetendstobemoreverbose,explicitlyloggingintermediatevisualstatesand
detailingparameters(e.g.,pre_dis_axis=’fp’,is_open=True),whilehuman-writtenscriptsare
moreminimal,omittingintermediatestepsandfavoringcompactexecution. Despitefunctionalsimi-
larity,thestructuraldifferencesillustratethatMLLM-generatedprogramsarenotonlyexecutable
butemphasizestep-by-stepclarity,contributingtomorerobustfeedbackandrepair.
H TaskInstructionandObjectDescriptionExample
InstructionTemplates(task: ‘PickDualBottles’)
"Use {a} to place {A} left of {B}.", "Set {A} to the left of {B}.", "Move {A} beside {B} using
{a}.", "Place {A} on {B}’s left side.", "Using {a}, position {A} next to {B}.", "Stick {A} on the
left of {B}.", "Use {a} and place {A} on {B}’s left.", etc
ObjectDescription
# object id - ‘001_bottle/0’:
"red bottle", "red soda bottle", "plastic red bottle", "red bottle with yellow label", "red
plastic bottle with smooth surface", "yellow text printed on red bottle surface", "red bottle with
white label design and markings", "red bottle with white sealing and brown top screw cap", etc
# object id - ‘039_mug/0’:
"black mug", "dark coffee mug", "sleek black mug", "black ceramic mug", "single-handle mug",
"smooth black surface mug", "medium-sized drinking mug", "round mug with curved side", "dark mug
with sturdy handle", "solid black mug with smooth finish", etc
I PromptsforGeneratingTaskInstructionsandObjectDescriptions
# Task Instruction Template
- Goal: Generate task instruction template
- Requirements:
- Generate 60 items. Vary in sentence length and structure
- Use natural action verbs (grab, slide, place)
- split
- 50 items for training
- 10 items for evaluation
## Schema Requirements
21

--- Page 22 ---
- Goal: Use placeholders for objects in instructions
- Requirements:
- Format: {X} for objects defined in schema
- Include all object placeholders ({A-Z}) in every instruction
- Omit arm references and placeholders ({a-z}) in 50% of instructions
- Ensure natural flow when placeholders are replaced with actual values
# Object Description
- Goal: Generate natural object descriptions for robotic manipulation
- Requirements:
- Generate 15 items. Vary in sentence length and structure
- Use natural oral language
- Include essential physical properties (color, shape, size, texture)
- Use noun-focused phrases
- For multi-part objects, use structures like ‘X with Y’
- split
- 12 items for training
- 3 items for evaluation
# Episode
An episode is a specified task, in which each task may have different objects to be
manipulated,
resulting in the same task template being reused by replacing the placeholders with
specific objects.
For example:
{A} -> ‘medium-sized yellow bottle’
{A} -> ‘green drink bottle with bold labels’
General Task -> Specific Episode:
{A} -> bottle/0.glb
{A} -> bottle/1.glb
The number of task instructions for an episode can be calculated by:
Episode_num = TaskInstruction_num * ObjectDescription_num
Listing3: PromptsforGeneratingTaskInstructionsandObjectDescriptions
J RoboTwin2.0BenchmarkSettingVisualization
We visualize the simulation settings of the RoboTwin 2.0 benchmark in Fig. 12. All models are
trainedon50clean(non-randomized)demonstrationspertask(blue). Forevaluation,theEasysetting
alsousescleanenvironments,whiletheHard settingemploysdomain-randomizedenvironments
(green).
Train (Easy + Hard)
Eval (Easy) Eval (Hard)
Figure12: HeterogeneousDual-ArmControlviaObject-CentricManipulation.
22

--- Page 23 ---
K FullRoboTwin2.0Benchmark
WereporttheevaluationresultsoffivepoliciesontheRoboTwin2.0benchmarkundertheEasyand
Hardsettings. Notethatthesetwosettingsdifferonlyinevaluationconditions,whilethetraining
setupremainsidentical.Acontinuouslymaintainedonlineleaderboardisavailableathttps://robotwin-
platform.github.io/leaderboard.
Table10: RoboTwin2.0SimulationBenchmark(cleanvsrandomized,50+tasks).
SimulationTask RDT Pi0 ACT DP DP3
Easy Hard Easy Hard Easy Hard Easy Hard Easy Hard
AdjustBottle 81% 75% 90% 56% 97% 23% 97% 0% 99% 3%
BeatBlockHammer 77% 37% 43% 21% 56% 3% 42% 0% 72% 8%
BlocksRankingRGB 3% 0% 19% 5% 1% 0% 0% 0% 3% 0%
BlocksRankingSize 0% 0% 7% 1% 0% 0% 1% 0% 2% 0%
ClickAlarmclock 61% 12% 63% 11% 32% 4% 61% 5% 77% 14%
ClickBell 80% 9% 44% 3% 58% 3% 54% 0% 90% 0%
DumpBinBigbin 64% 32% 83% 24% 68% 1% 49% 0% 85% 53%
GrabRoller 74% 43% 96% 80% 94% 25% 98% 0% 98% 2%
HandoverBlock 45% 14% 45% 8% 42% 0% 10% 0% 70% 0%
HandoverMic 90% 31% 98% 13% 85% 0% 53% 0% 100% 3%
HangingMug 23% 16% 11% 3% 7% 0% 8% 0% 17% 1%
LiftPot 72% 9% 84% 36% 88% 0% 39% 0% 97% 0%
MoveCanPot 25% 12% 58% 21% 22% 4% 39% 0% 70% 6%
MovePillbottlePad 8% 0% 21% 1% 0% 0% 1% 0% 41% 0%
MovePlayingcardAway 43% 11% 53% 22% 36% 0% 47% 0% 68% 3%
MoveStaplerPad 2% 0% 0% 2% 0% 0% 1% 0% 12% 0%
OpenLaptop 59% 32% 85% 46% 56% 0% 49% 0% 82% 7%
OpenMicrowave 37% 20% 80% 50% 86% 0% 5% 0% 61% 22%
PickDiverseBottles 2% 0% 27% 6% 7% 0% 6% 0% 52% 1%
PickDualBottles 42% 13% 57% 12% 31% 0% 24% 0% 60% 1%
PlaceA2BLeft 3% 1% 31% 1% 1% 0% 2% 0% 46% 2%
PlaceA2BRight 1% 1% 27% 6% 0% 0% 13% 0% 49% 0%
PlaceBreadBasket 10% 2% 17% 4% 6% 0% 14% 0% 26% 1%
PlaceBreadSkillet 5% 1% 23% 1% 7% 0% 11% 0% 19% 0%
PlaceBurgerFries 50% 27% 80% 4% 49% 0% 72% 0% 72% 18%
PlaceCanBasket 19% 6% 41% 5% 1% 0% 18% 0% 67% 2%
PlaceCansPlasticbox 6% 5% 34% 2% 16% 0% 40% 0% 48% 3%
PlaceContainerPlate 78% 17% 88% 45% 72% 1% 41% 0% 86% 1%
PlaceDualShoes 4% 4% 15% 0% 9% 0% 8% 0% 13% 0%
PlaceEmptyCup 56% 7% 37% 11% 61% 0% 37% 0% 65% 1%
PlaceFan 12% 2% 20% 10% 1% 0% 3% 0% 36% 1%
PlaceMousePad 1% 0% 7% 1% 0% 0% 0% 0% 4% 1%
PlaceObjectBasket 33% 17% 16% 2% 15% 0% 15% 0% 65% 0%
PlaceObjectScale 1% 0% 10% 0% 0% 0% 1% 0% 15% 0%
PlaceObjectStand 15% 5% 36% 11% 1% 0% 22% 0% 60% 0%
PlacePhoneStand 15% 6% 35% 7% 2% 0% 13% 0% 44% 2%
PlaceShoe 35% 7% 28% 6% 5% 0% 23% 0% 58% 2%
PressStapler 41% 24% 62% 29% 31% 6% 6% 0% 69% 3%
PutBottlesDustbin 21% 4% 54% 13% 27% 1% 22% 0% 60% 21%
PutObjectCabinet 33% 18% 68% 18% 15% 0% 42% 0% 72% 1%
RotateQRcode 50% 5% 68% 15% 1% 0% 13% 0% 74% 1%
ScanObject 4% 1% 18% 1% 2% 0% 9% 0% 31% 1%
ShakeBottleHorizontally 84% 51% 99% 51% 63% 4% 59% 18% 100% 25%
ShakeBottle 74% 45% 97% 60% 74% 10% 65% 8% 98% 19%
StackBlocksThree 2% 0% 17% 0% 0% 0% 0% 0% 1% 0%
StackBlocksTwo 21% 2% 42% 1% 25% 0% 7% 0% 24% 0%
StackBowlsThree 51% 17% 66% 24% 48% 0% 63% 0% 57% 5%
StackBowlsTwo 76% 30% 91% 41% 82% 0% 61% 0% 83% 6%
StampSeal 1% 0% 3% 4% 2% 0% 2% 0% 18% 0%
TurnSwitch 35% 15% 27% 23% 5% 2% 36% 1% 46% 8%
Average(%) 34.5 13.7 46.4 16.3 29.7 1.7 28.0 0.6 55.2 5.0
23

--- Page 24 ---
L SuccessRatesofDifferentEmbodimentsonRoboTwin2.0Tasks
Table11reportsthesuccessratesoffiverobotembodimentsacrossthe50RoboTwin2.0tasks,using
thesamesetofexpertprogramsfordatageneration.
Table11: SuccessRatesofDifferentEmbodimentsonRoboTwin2.0Tasks.
RoboTwin1.0 RoboTwin2.0
TaskName Aloha ARX Franka Piper UR5 Aloha ARX Franka Piper UR5
AdjustBottle 92% 88% 39% 0% 7% 93% 94% 34% 0% 12%
BeatBlockHammer 68% 86% 95% 0% 86% 64% 93% 98% 15% 90%
BlocksRankingRgb 92% 98% 96% 0% 82% 96% 97% 99% 13% 53%
BlocksRankingSize 90% 95% 92% 0% 60% 96% 97% 89% 7% 38%
ClickAlarmclock 89% 99% 100% 0% 95% 92% 99% 100% 0% 95%
ClickBell 100% 100% 100% 9% 100% 100% 100% 100% 91% 100%
DumpBinBigbin 85% 98% 90% 0% 82% 84% 100% 84% 9% 80%
GrabRoller 95% 69% 99% 0% 80% 95% 69% 99% 7% 81%
HandoverBlock 1% 3% 0% 0% 4% 83% 81% 0% 44% 0%
HandoverMic 62% 80% 92% 28% 0% 87% 98% 84% 65% 14%
HangingMug 68% 76% 5% 0% 12% 63% 73% 11% 0% 11%
LiftPot 27% 50% 24% 5% 40% 27% 50% 36% 31% 40%
MoveCanPot 18% 0% 37% 2% 4% 93% 65% 92% 96% 99%
MovePillbottlePad 30% 52% 15% 0% 35% 67% 90% 69% 47% 86%
MovePlayingcardAway 93% 100% 100% 0% 87% 99% 100% 100% 63% 66%
MoveStaplerPad 94% 92% 88% 0% 95% 92% 96% 89% 13% 75%
OpenLaptop 76% 91% 78% 14% 55% 82% 92% 77% 23% 51%
OpenMicrowave 65% 85% 75% 5% 33% 96% 80% 59% 2% 23%
PickDiverseBottles 11% 1% 0% 0% 0% 51% 2% 0% 27% 4%
PickDualBottles 8% 3% 0% 0% 0% 92% 6% 0% 81% 7%
PlaceA2BLeft 65% 75% 70% 0% 72% 80% 88% 64% 29% 76%
PlaceA2BRight 70% 68% 68% 0% 69% 81% 82% 64% 31% 66%
PlaceBreadBasket 91% 91% 69% 0% 78% 89% 88% 62% 1% 67%
PlaceBreadSkillet 31% 28% 42% 0% 42% 34% 26% 42% 0% 37%
PlaceCanBasket 47% 1% 38% 0% 11% 70% 28% 61% 0% 3%
PlaceCansPlasticbox 96% 93% 98% 0% 11% 100% 96% 85% 0% 82%
PlaceContainerPlate 86% 85% 83% 0% 82% 89% 86% 86% 37% 81%
PlaceDualShoes 73% 28% 36% 0% 40% 77% 31% 41% 1% 32%
PlaceEmptyCup 92% 100% 100% 0% 100% 92% 100% 100% 4% 100%
PlaceFan 93% 96% 75% 0% 85% 95% 93% 83% 0% 65%
PlaceBurgerFries 96% 95% 85% 0% 78% 97% 98% 80% 36% 74%
PlaceMousePad 100% 80% 99% 2% 96% 99% 89% 100% 23% 73%
PlaceObjectBasket 68% 13% 68% 0% 30% 74% 14% 61% 0% 7%
PlaceObjectScale 77% 93% 94% 0% 87% 78% 92% 82% 2% 76%
PlaceObjectStand 90% 92% 81% 0% 90% 97% 99% 81% 9% 92%
PlacePhoneStand 66% 78% 52% 22% 44% 66% 78% 45% 53% 49%
PlaceShoe 87% 85% 70% 0% 97% 84% 85% 74% 7% 91%
PressStapler 87% 96% 99% 0% 77% 98% 96% 100% 59% 72%
PutBottlesDustbin 0% 0% 0% 0% 0% 71% 1% 0% 56% 0%
PutObjectCabinet 13% 56% 43% 0% 0% 14% 24% 55% 0% 0%
RotateQrcode 78% 83% 98% 0% 81% 75% 74% 94% 0% 67%
ScanObject 8% 13% 21% 0% 8% 4% 45% 26% 0% 19%
ShakeBottle 62% 95% 82% 1% 98% 89% 94% 85% 74% 97%
ShakeBottleHorizontally 64% 93% 81% 1% 97% 90% 94% 85% 74% 98%
StackBlocksThree 98% 97% 95% 0% 83% 94% 96% 80% 0% 51%
StackBlocksTwo 99% 99% 100% 0% 94% 98% 99% 96% 2% 68%
StackBowlsThree 27% 64% 76% 0% 76% 43% 58% 82% 0% 81%
StackBowlsTwo 63% 84% 88% 0% 94% 78% 82% 88% 4% 94%
StampSeal 46% 91% 95% 0% 100% 56% 91% 4% 37% 100%
TurnSwitch 27% 3% 51% 28% 10% 74% 3% 36% 81% 10%
Average 65.3% 68.8% 67.6% 2.3% 57.7% 78.8% 74.2% 67.2% 25.1% 57.1%
Difference / / / / / +13.5% +5.4% -0.4% +22.8% -0.6%
24