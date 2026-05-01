--- Page 1 ---
Preprint
RT-1: ROBOTICS TRANSFORMER
FOR REAL-WORLD CONTROL AT SCALE
1AnthonyBrohan∗,NoahBrown∗,JusticeCarbajal∗,YevgenChebotar∗,JosephDabis∗,
ChelseaFinn∗,KeerthanaGopalakrishnan∗,KarolHausman∗,AlexHerzog†,JasmineHsu∗,
JulianIbarz∗,BrianIchter∗,AlexIrpan∗,TomasJackson∗,SallyJesmonth∗,NikhilJJoshi∗,
RyanJulian∗,DmitryKalashnikov∗,YuhengKuang∗,IsabelLeal∗,Kuang-HueiLee‡,SergeyLevine∗,
YaoLu∗,UtsavMalla∗,DeekshaManjunath∗,IgorMordatch‡,OfirNachum‡,CarolinaParada∗,
JodilynPeralta∗,EmilyPerez∗,KarlPertsch∗,JornellQuiambao∗,KanishkaRao∗,MichaelRyoo∗,
GreciaSalazar∗,PannagSanketi∗,KevinSayed∗,JaspiarSingh∗,SumedhSontakke‡,AustinStone∗,
ClaytonTan∗,HuongTran∗,VincentVanhoucke∗,SteveVega∗,QuanVuong∗,FeiXia∗,TedXiao∗,
PengXu∗,SichunXu∗,TianheYu∗,BriannaZitkovich∗
∗RoboticsatGoogle,†EverydayRobots,‡GoogleResearch,BrainTeam
ABSTRACT
Bytransferringknowledgefromlarge,diverse,task-agnosticdatasets,modernma-
chinelearningmodelscansolvespecificdownstreamtaskseitherzero-shotorwith
smalltask-specificdatasetstoahighlevelofperformance. Whilethiscapability
has been demonstrated in other fields such as computer vision, natural language
processing or speech recognition, it remains to be shown in robotics, where the
generalization capabilities of the models are particularly critical due to the dif-
ficulty of collecting real-world robotic data. We argue that one of the keys to
the success of such general robotic models lies with open-ended task-agnostic
training,combinedwithhigh-capacityarchitecturesthatcanabsorballofthedi-
verse, robotic data. In this paper, we present a model class, dubbed Robotics
Transformer, that exhibits promising scalable model properties. We verify our
conclusionsinastudyofdifferentmodelclassesandtheirabilitytogeneralizeas
a function of the data size, model size, and data diversity based on a large-scale
datacollectiononrealrobotsperformingreal-worldtasks. Theproject’swebsite
andvideoscanbefoundatrobotics-transformer1.github.io
1 INTRODUCTION
End-to-end robotic learning, with either imitation or reinforcement, typically involves collecting
task-specific data in either single-task (Kalashnikov et al., 2018; Zhang et al., 2018) or multi-
task (Kalashnikov et al., 2021b; Jang et al., 2021) settings that are narrowly tailored to the tasks
thattherobotshouldperform. Thisworkflowmirrorstheclassicapproachtosupervisedlearningin
otherdomains,suchascomputervisionandNLP,wheretask-specificdatasetswouldbecollected,
labeled, and deployed to solve individual tasks, with little interplay between the tasks themselves.
Recentyearshaveseenatransformationinvision,NLP,andotherdomains,awayfromsiloed,small-
scale datasets and models and towards large, general models pre-trained on broad, large datasets.
Thekeystothesuccessofsuchmodelsliewithopen-endedtask-agnostictraining,combinedwith
high-capacityarchitecturesthatcanabsorballoftheknowledgepresentinlarge-scaledatasets. Ifa
model can “sponge up” experience to learn general patterns in language or perception, then it can
bring them to bear on individual tasks more efficiently. While removing the need for large task-
specific datasets is appealing generally in supervised learning, it is even more critical in robotics,
wheredatasetsmightrequireengineering-heavyautonomousoperationorexpensivehumandemon-
strations. Wethereforeask: canwetrainasingle,capable,largemulti-taskbackbonemodelondata
consistingofawidevarietyofrobotictasks? Anddoessuchamodelenjoythebenefitsobservedin
otherdomains,exhibitingzero-shotgeneralizationtonewtasks,environments,andobjects?
Buildingsuchmodelsinroboticsisnoteasy. Althoughrecentyearshaveseenseverallargemulti-
taskrobotpoliciesproposedintheliterature(Reedetal.,2022;Jangetal.,2021),suchmodelsoften
havelimitedbreadthofreal-worldtasks,aswithGato(Reedetal.,2022),orfocusontrainingtasks
ratherthangeneralizationtonewtasks,aswithrecentinstructionfollowingmethods(Shridharetal.,
2021;2022),orattaincomparativelylowerperformanceonnewtasks(Jangetal.,2021).
1Authorslistedinalphabeticalorder.ContributionsinAppendixA.
Correspondingemails:{keerthanapg,kanishkarao,karolhausman}@google.com.
1
3202
guA
11
]OR.sc[
2v71860.2122:viXra

--- Page 2 ---
Instruction
Pick apple from top drawer and place on counter Mode Arm Base
Images
FiLM
EfficientNet TokenLearner Transformer
Preprint
…
RT-1
3 Hz
β
)γ+1(
Action
·
+
Instruction
Pick apple from top drawer and place on counter Mode Arm Base
Images
FiLM
EfficientNet TokenLearner Transformer
…
RT-1
3 Hz
β
)γ+1(
Action
·
+
(a)RT-1takesimagesandnaturallanguageinstructionsandoutputsdiscretizedbaseandarmactions. Despite
itssize(35Mparameters),itdoesthisat3Hz,duetoitsefficientyethigh-capacityarchitecture:aFiLM(Perez
et al., 2018) conditioned EfficientNet (Tan & Le, 2019), a TokenLearner (Ryoo et al., 2021), and a Trans-
former(Vaswanietal.,2017).
(b)RT-1’slarge-scale,real-worldtraining(130kdemonstrations)andevaluation(3000real-worldtrials)show
impressivegeneralization,robustness,andabilitytolearnfromdiversedata.
Figure1: Ahigh-leveloverviewofRT-1’sarchitecture,dataset,andevaluation.
Thetwomainchallengesliein assemblingtherightdatasetanddesigningtherightmodel. While
data collection and curation is often the “unsung hero” of many large-scale machine learning
projects(Radfordetal.,2021;Rameshetal.,2021),thisisespeciallytrueinrobotics,wheredatasets
areoftenrobot-specificandgatheredmanually(Dasarietal.,2019;Ebertetal.,2021). Aswewill
showinourevaluations,goodgeneralizationrequiresdatasetsthatcombinebothscaleandbreadth,
coveringavarietyoftasksandsettings. Atthesametime, thetasksinthedatasetshouldbesuffi-
ciently well-connected to enable generalization, such that the model can discover the patterns be-
tweenstructuralsimilartasksandperformnewtasksthatcombinethosepatternsinnovelways. We
utilizeadatasetthatwegatheredoverthecourseof17monthswithafleetof13robots,containing
∼130kepisodesandover700tasks,andweablatevariousaspectsofthisdatasetinourevaluation.
The second challenge lies in the design of the model itself. Effective robotic multi-task learning
requiresahighcapacitymodel,andTransformer(Vaswanietal.,2017)modelsexcelinthisregard,
particularlywhenitisnecessarytolearnmanytasksconditioned,asinourcase,onlanguageinstruc-
tions. However,roboticcontrollersmustalsobeefficientenoughtoruninrealtime,whichpresents
amajorchallengeforTransformersinparticular. WeproposeanovelarchitecturethatwecallRT-1
(RoboticsTransformer1),whichbyencodinghigh-dimensionalinputsandoutputs,includingcam-
eraimages,instructionsandmotorcommandsintocompacttokenrepresentationstobeusedbythe
Transformer,allowsforefficientinferenceatruntimetomakereal-timecontrolfeasible.
OurcontributionistheRT-1modelandexperimentswiththismodelonalargeandbroaddatasetof
real-worldrobotictasks. OurexperimentsnotonlydemonstratethatRT-1canexhibitsignificantly
improvedgeneralizationandrobustnesscomparedtopriortechniques,butalsoevaluateandablate
manydesignchoicesinboththemodelandinthecompositionofthetrainingset. Ourresultsshow
thatRT-1canperformover700traininginstructionsat97%successrate,andcangeneralizetonew
tasks, distractors, and backgrounds 25%, 36% and 18% better than the next best baseline, respec-
tively. Thislevelofperformanceallowsustoexecuteverylong-horizontasksintheSayCan(Ahn
etal.,2022)framework,withasmanyas50stages. WefurthershowthatRT-1canincorporatedata
fromsimulationorevenotherrobottypes,retainingperformanceontheoriginaltasksandimproving
generalizationtonewscenarios. AshortoverviewofRT-1capabilitiesispresentedinFig.1b2.
2HelperrobotsshowninFig.1-5arefromEverydayRobots
2

--- Page 3 ---
Preprint
2 RELATED WORK
A number of recent works have proposed Transformer-based policies for robotic control. As in
RT-1, several works use language commands processed with Transformers as a robust framework
for specifying and generalizing to new tasks (Zhang & Chai, 2021; Pashevich et al., 2021; Silva
et al., 2021; Jang et al., 2021; Ahn et al., 2022; Nair et al., 2022). Our work takes the application
ofTransformersastepfurtherandtreatsthemappingoflanguageandvisionobservationstorobot
actions as a sequence modelling problem, using a Transformer to learn this mapping. This idea
is directly inspired by successes in game-playing (Chen et al., 2021; Lee et al., 2022a) as well
as simulated robot navigation (Fang et al., 2019), locomotion (Janner et al., 2021; Gupta et al.,
2022),andmanipulation(Jiangetal.,2022)environments. Wenotethatseveraloftheseworksgo
beyond only text conditioning and use Transformers to also generalize across robot morphologies
(e.g.,Guptaetal.(2022))andothermodalitiesfortaskspecifications(e.g.,Jangetal.(2021);Jiang
etal.(2022)). TheseextensionsarepromisingfuturedirectionsforRT-1.
BeyondTransformer-basedpolicies,thefocusofourworkisongeneralizableandrobustreal-world
roboticmanipulationatscale.Existingworksonreal-worldTransformer-basedroboticmanipulation
focus on efficiently learning tasks from a set of demonstrations per task (Shridhar et al., 2022).
Behavior Transformer (Shafiullah et al., 2022) and Gato (Reed et al., 2022) advocate for training
a single model on large-scale robotic and non-robotic datasets. However, these works are limited
intheirreal-worldrobotictasks;e.g.,Gatolearnseffectivelyasingletask(coloredblockstacking)
withoutevaluatinggeneralizationtonewtasksoravarietyofreal-worldsettings. Onthetechnical
side,ourworkexamineshowTransformer-basedpoliciescanbebuiltsoastocombinehighcapacity
andgeneralizationwiththecomputationalefficiencynecessaryforreal-timecontrol.
Whiletheuseofhigh-capacityTransformermodelstolearnroboticcontrolpoliciesisafairlyrecent
innovation, robotics has a long history of multi-task and language-conditioned learning, and RT-1
buildsonthesefoundations. Asignificantbodyofworkdealswithlearningpoliciesandpredictive
models for robotic grasping (Saxena et al., 2006; Lenz et al., 2015; Pinto & Gupta, 2016; Gupta
et al., 2018; Viereck et al., 2017), with the aim of generalizing to new objects. Prior works have
sought to address robotic language understanding through pipelined approaches that combine lan-
guageparsing,vision,androboticcontrol(MacMahonetal.,2006;Kollaretal.,2010;Tellexetal.,
2011)andwithend-to-endapproaches(Meietal.,2016;Stepputtisetal.,2020;Lynch&Sermanet,
2020;Ahnetal.,2022). Multi-taskroboticlearninghasalsobeenapproachedfromtheperspective
of learning to reach goals (Chung et al., 2015; Raffin et al., 2019; Jurgenson et al., 2020; Huang
etal.,2020), aswellaslearningpoliciesthatcanperformtasksinadiscretesetorsomeotherpa-
rameterizedform(Deisenrothetal.,2014;Devinetal.,2017;Foxetal.,2019;Kalashnikovetal.,
2021a). A number of prior works in robotics have also focused on collecting datasets containing
demonstrationsortrialsthatillustrateavarietyofdifferenttasks(Sharmaetal.,2018;Dasarietal.,
2019; Yu et al., 2020; Singh et al., 2020; James et al., 2020). Our work adds further evidence in
supportofthepowerofmulti-task,language-conditionedroboticlearning,presentingexperimental
results at a larger scale and with a greater variety of behaviors, objects, and scenes and proposing
newarchitecturesanddesignchoicesthatenableroboticlearningatasignificantlylargerscale.
3 PRELIMINARIES
Robotlearning. Weaimtolearnrobotpoliciestosolvelanguage-conditionedtasksfromvision.
Formally,weconsiderasequentialdecision-makingenvironment. Attimestept = 0,thepolicyπ
ispresentedwithalanguageinstructioniandaninitialimageobservationx . Thepolicyproduces
0
an action distribution π(· | i,x ) from which an action a is sampled and applied to the robot.
0 0
Thisprocesscontinues,withthepolicyiterativelyproducingactionsa bysamplingfromalearned
t
distributionπ(·|i,{x }t )andapplyingthoseactionstotherobot. Theinteractionendswhena
j j=0
terminationconditionisachieved. Thefullinteractioni,{(x ,a )}T fromfromthestartingstep
j j j=0
t = 0 to terminating step T is referred to as an episode. At the end of an episode, the agent will
begivenabinaryrewardr ∈ {0,1}indicatingwhethertherobotperformedtheinstructioni. The
goalistolearnapolicyπ thatmaximizestheaveragereward,inexpectationoveradistributionof
instructions,startingstatesx ,andtransitiondynamics.
0
3

--- Page 4 ---
Preprint
Transformers. RT-1usesaTransformer(Vaswanietal.,2017)toparameterizethepolicyπ. Gener-
allyspeaking,aTransformerisasequencemodelmappinganinputsequence{ξ }H toanoutput
h h=0
sequence{y }K usingcombinationsofself-attentionlayersandfully-connectedneuralnetworks.
k k=0
WhileTransformerswereoriginallydesignedfortextsequences,whereeachinputξ andoutputy
j k
represents a text token, they have been extended to images (Parmar et al., 2018) as well as other
modalities (Lee et al., 2022a; Reed et al., 2022). As detailed in the next section, we parameterize
π by first mapping inputs i,{x }t to a sequence {ξ }H and action outputs a to a sequence
j j=0 h h=0 t
{y }K beforeusingaTransformertolearnthemapping{ξ }H →{y }K .
k k=0 h h=0 k k=0
Imitation learning. Imitation learning methods train the policy π on a dataset D of demonstra-
tions (Pomerleau, 1988; Zhang et al., 2018; Jang et al., 2021). Specifically, we assume access to
adatasetD = {(i(n),{(x(n),a(n))}T(n))}N ofepisodes,allofwhicharesuccessful(i.e.,havea
t t t=0 n=0
finalrewardof1). Welearnπ usingbehavioralcloning(Pomerleau,1988), whichoptimizesπ by
minimizingthenegativelog-likelihoodofactionsa giventheimagesandlanguageinstructions.
t
4 SYSTEM OVERVIEW
The goal of this work is to build and demonstrate a general robot learning system that can ab-
sorblargeamountsofdataandgeneralizeeffectively. WeusemobilemanipulatorsfromEveryday
Robots3, which have a 7 degree-of-freedom arm, a two-fingered gripper, and a mobile base (see
Fig.2(d)). Tocollectdataandevaluateourmethod,weusethreekitchen-basedenvironments: two
real office kitchens and a training environment modelled off these real kitchens. The training en-
vironment, shown in Fig. 2 (a), consists of partial counters and is constructed for large scale data
collection. Thetworealenvironments,showninFig.2(b,c),havesimilarcountertopstothetrain-
ingenvironment,butvaryinlighting,background,andfullkitchengeometry(e.g.,theremaybea
cabinetinsteadofadrawerorasinkmaybevisible). Weevaluatetheperformanceofourpolicies
acrossthesedifferentenvironments,measuringthepolicy’sperformanceandabilitytogeneralize.
Ourtrainingdataconsistsofhuman-provideddemonstrations,andweannotateeachepisodewitha
textualdescriptionoftheinstructionthattherobotjustperformed. Theinstructionsusuallycontain
averbandoneormorenounsdescribingthetargetobjects. Togrouptheseinstructionstogether,we
splitthemintoanumberofskills(e.g.,verbssuchas“pick”,“open”or“placeupright”)andobjects
(e.g., nounssuchas“cokecan”, “apple”, or“drawer”). Wedescribethedetailsofourdatacollec-
tionstrategyatscaleinSec.5.2. Ourlargestdatasetcontainsover130kindividualdemonstrations
constitutingover700distincttaskinstructionsusingalargevarietyofobjects(seeFig.2(f)). We
describethedetailsofthedatacollectedinSec.5.2.
One of the main contributions of our system is the network architecture, Robotics Transformer 1
(RT-1),anefficientmodelthatcanabsorblargeamountsofdata,effectivelygeneralize,andoutput
actions at real-time rates for practical robotic control. RT-1 takes a short sequence of images and
a natural language instruction as input and outputs an action for the robot at each time step. To
this end, the architecture (shown in Figure 1a) leverages several elements: first the images and
textareprocessedviaanImageNetpretrainedconvolutionalnetwork(Tan&Le,2019)conditioned
on a pretrained embedding of the instruction via FiLM (Perez et al., 2018), followed by a Token
Learner(Ryooetal.,2021)tocomputeacompactsetoftokens,andfinallyaTransformer(Vaswani
etal.,2017)toattendoverthesetokensandproducediscretizedactiontokens. Theactionsconsist
ofsevendimensionsforthearmmovement(x, y, z, roll, pitch, yaw, openingofthegripper), three
dimensionsforbasemovement(x,y,yaw)andadiscretedimensiontoswitchbetweenthreemodes:
controlling the arm, the base, or terminating the episode. RT-1 performs closed-loop control and
commandsactionsat3Hzuntiliteitheryieldsa“terminate”actionorhitsapre-settimesteplimit.
5 RT-1: ROBOTICS TRANSFORMER
Inthissection,wedescribehowwetokenizetheimages,text,andactions,andthendiscusstheRT-1
modelarchitecture.Wethendescribehowweattaintheruntimespeedrequiredforreal-timecontrol.
Lastly,wedescribethedatacollectionprocedureandtheskillsandinstructionsinourdataset.
3everydayrobots.com
4

--- Page 5 ---
Preprint
Figure2:(a)Robotclassroomwherewecollectdataatscale;(b)arealofficekitchen,oneofthetwo
realisticenvironmentsusedforevaluation(namedKitchen1intherestofthepaper);(c)adifferent
officekitchenusedforevaluation(namedKitchen2intherestofthepaper);(d)mobilemanipulator
usedthroughoutthepaper; (e)asetofobjectsusedformostoftheskillstoexpandskilldiversity;
(f)amorediversesetofobjectsusedmostlytoexpandobjectdiversityofthepickingskill.
5.1 MODEL
OurmodelisbuiltonaTransformerarchitecture(Vaswanietal.,2017)andtakesahistoryofimages
andtaskdescriptionasinputanddirectlyoutputstokenizedactions,asshowninFig.1aandindetail
in Fig. 3. In the following we describe the components of the model, following the top-to-bottom
orderinFig.3. MoredetailonmodelselectionatscaleareprovidedinAppendixC.3.
Instructionandimagetokenization. TheRT-1architecturereliesonadata-efficientandcompact
tokenizationofimagesand languageinstruction. RT-1tokenizesahistoryof6imagesbypassing
images through an ImageNet pretrained EfficientNet-B3 (Tan & Le, 2019) model, which takes 6
imagesofresolution300×300asinputandoutputsaspatialfeaturemapofshape9×9×512from
the final convolutional layer. Unlike Reed et al. (2022), we do not patchify the images into visual
tokenspriortofeedingthemtoourTransformerbackbone.Weinsteadflattentheoutputfeaturemap
fromtheEfficientNetinto81visualtokenswhicharepassedontothelaterlayersofthenetwork.
To include the language instruction, we condition the image tokenizer on the natural language in-
structionintheformofapretrainedlanguageembedding,allowingextractionoftask-relevantimage
featuresearlyonandimprovingperformanceofRT-1. TheinstructionisfirstembeddedviaUniver-
salSentenceEncoder(Ceretal.,2018). Thisembeddingisthenusedasinputtoidentity-initialized
FiLM layers (Perez et al., 2018) added to the pretrained EfficientNet to condition the image en-
coder. Normally,insertingaFiLMlayerintotheinteriorofapretrainednetworkwoulddisruptthe
intermediate activations and negate the benefit of using pretrained weights. To overcome this, we
initialize the weights of the dense layers (f and h ) which produce the FiLM affine transforma-
c C
tiontozero,allowingtheFiLMlayertoinitiallyactasanidentityandpreservethefunctionofthe
pretrainedweights. Wefindthatidentity-initializedFiLMalsoproducesbetterresultswhentraining
withanEfficientNetinitializedfromscratch,withoutImageNetpretraining,butitdoesnotsurpass
theinitializationdescribedabove. ThearchitectureoftheimagetokenizerispresentedinFig.3.
RT-1’simageandinstructiontokenizationviaFiLMEfficientNet-B3isatotalof16Mparameters,
with26layersofMBConvblocksandFiLMlayers,whichoutput81vision-languagetokens.
TokenLearner. TofurthercompressthenumberoftokensthatRT-1needstoattendoverandthus
speed up inference, RT-1 uses TokenLearner (Ryoo et al., 2021). TokenLearner is an element-
wise attention module that learns to map a large number of tokens into a much smaller number
of tokens. This allows us to soft-select image tokens based on their information, passing only the
importanttokencombinationstothesubsequentTransformerlayers. TheinclusionofTokenLearner
subsamplesthe81visualtokensthatcomeoutofthepre-trainedFiLM-EfficientNetlayerstojust8
finaltokensthatarethenpassedontoourTransformerlayers.
5

--- Page 6 ---
Preprint
1 γ) β
· + …
1 γ) β
1 γ) β
1 γ) β
Figure3: ThearchitecturediagramofRT-1. TheinstructionistransformedintoaUSEembedding
and used to condition a pre-trained EfficientNet via FiLM layers. The resulting vision-language
tokens are reduced by the TokenLearner and fed into a decoder-only Transformer, which outputs
tokenizedactions.
Transformer. These8tokensper-imagearethenconcatenatedwiththeotherimagesinthehistory,
forming48totaltokens(withaddedpositionencoding)tobefedintotheTransformerbackboneof
RT-1. TheTransformerisadecoder-onlysequencemodelwith8self-attentionlayersand19Mtotal
parametersthatoutputsactiontokens.
Action tokenization. To tokenize actions, each action dimension in RT-1 is discretized into 𝜸𝜷
256 bins. As mentioned previously, the action dimensions we consider include seven variables
for the arm movement (x, y, z, roll, pitch, yaw, opening of the gripper), three variables for base
movement(x,y,yaw)andadiscretevariabletoswitchbetweenthreemodes: controllingarm,base
orterminatingtheepisode. Foreachvariable,wemapthetargettooneofthe256bins,wherethe
binsareuniformlydistributedwithintheboundsofeachvariable.
Loss. We use a standard categorical cross-entropy entropy objective and causal masking that was
utilizedinpriorTransformer-basedcontrollers(Reedetal.,2022;Leeetal.,2022a).
Inference speed. In contrast to many applications of large models, such as natural language or
imagegeneration,oneoftheuniquerequirementsforamodelthatneedstorunonrealrobotsinreal
time is fast and consistent inference speed. Given the human speeds of executing the instructions
6

--- Page 7 ---
Preprint
consideredinthiswork(whichwemeasuredtobeinthe2−4secsrange),wewantthemodeltobe
notsignificantlyslowerthanthat. Basedonourexperimentsthisrequirementcorrespondstoatleast
3Hzcontrolfrequencyandtheresultinginferencetimebudgetforthemodel,givenotherlatencies
inthesystem,tobelessthan100ms.
This requirement limits the size of the model that we can use. We further explore the impact of
modelsizeoninferencespeedintheexperiments. Weemploytwotechniquestospeedupinference:
(i) reduce the number of tokens generated by a pre-trained EfficientNet model by using Token-
Learner(Ryooetal.,2021), (ii)computethesetokensonlyonceandreusethemforthefollowing
windowsthatoverlapforthefutureinferences. Bothoftheseallowustospeedupthemodelinfer-
enceby2.4and1.7times,respectively. AdditionaldetailsonmodelinferenceareinAppendixC.1.
5.2 DATA
Skill Count Description ExampleInstruction
PickObject 130 Lifttheobjectoffthesurface pickicedteacan
MoveObjectNearObject 337 Movethefirstobjectnearthesecond movepepsicannearrxbarblueberry
PlaceObjectUpright 8 Placeanelongatedobjectupright placewaterbottleupright
KnockObjectOver 8 Knockanelongatedobjectover knockredbullcanover
OpenDrawer 3 Openanyofthecabinetdrawers openthetopdrawer
CloseDrawer 3 Closeanyofthecabinetdrawers closethemiddledrawer
PlaceObjectintoReceptacle 84 Placeanobjectintoareceptacle placebrownchipbagintowhitebowl
PickObjectfromReceptacle 162 Pickanobjectupfromalocationandthen pickgreenjalapenochipbagfrompaper
andPlaceontheCounter placeitonthecounter bowlandplaceoncounter
Section6.3and6.4tasks 9 Skillstrainedforrealistic,longinstructions openthelargeglassjarofpistachios
pullnapkinoutofdispenser
grabscooper
Total 744
Table 1: The list of skills collected for RT-1 together with their descriptions and example instruc-
tions.
Our goal is to build a system that exhibits high performance, generalization to new tasks, and ro-
bustnesstodistractorsandbackgrounds. Wethereforeaimtocollectalarge,diversedatasetofrobot
trajectoriesthatincludesmultipletasks,objectsandenvironments. Ourprimarydatasetconsistsof
∼130krobotdemonstrations,collectedwithafleetof13robotsoverthecourseof17months. We
conductedthislarge-scaledatacollectioninaseriesofofficekitchensegments,whichwerefertoas
robotclassrooms,showninFig.2. MoredetailsondatacollectionareinAppendixC.2.
Skills and instructions. While the definition of a task remains inconsistent in the literature, in
this work we count the number of language instructions that the system can perform, where an
instructioncorrespondstoaverbsurroundedbyoneormultiplenouns,suchas“placewaterbottle
upright”,“movethecokecantothegreenchipbag”or“openthedrawer”. RT-1isabletoperform
over700languageinstructionsinmultiplerealisticofficekitchenenvironmentsthatweevaluateand
describeindetailintheexperiments. Inordertogrouptheevaluationsanddrawconclusionsonthe
performanceofthesystem,wegrouptheinstructionsbytheverbsusedinthem,whichwereferto
asskills. AmoredetailedlistofinstructionsisshowninTable1,withexamplesandthenumberof
instructionsperskill.
Thecurrentsetofskillsincludespicking,placing,openingandclosingdrawers,gettingitemsinand
outdrawers,placingelongateditemsup-right,knockingthemover,pullingnapkinsandopeningjars.
Theskillswerechosentodemonstratemultiplebehaviorswithmanyobjects(seeninFig.2(e))to
testaspectsofRT-1suchasgeneralizationtonewinstructionsandabilitytoperformmanytasks.We
thengreatlyexpandedtheobjectdiversityforthe“pick”skilltomakesurethattheskillsgeneralize
to varied objects (see the expanded set of objects in Fig. 2(f)). The skills were further expanded
while we conducted the ablations to include instructions added in the last row of Table 1, which
were used for the experiments described in Sec. 6.4 and 6.3. These additional skills focused on
realistic,long-horizoninstructionsinanofficekitchen. Theentireprocessofaddingtasksanddata
is described in the Appendix C.4. Since we do not make any assumptions about particular skills
when adding new instructions, the system is easily extendable, and we can continuously provide
morediversedatatoimproveitscapabilities.
7

--- Page 8 ---
Preprint
6 EXPERIMENTS
Ourexperimentsseektoanswerthefollowingquestions:
1. Can an RT-1 learn to perform a large number of instructions, as well as to generalize in
zeroshottonewtasks,objectsandenvironments? (Section6.2)
2. Canwepushtheresultingmodelevenfurtherbyincorporatingheterogeneousdatasources,
suchassimulateddataordatafromdifferentrobots? (Section6.3)
3. Howdovariousmethodsgeneralizetolong-horizonroboticscenarios? (Section6.4)
4. How do generalization metrics change with varying amounts of data quantity and data
diversity? (Section6.5)
5. Whataretheimportantandpracticaldecisionsinthedesignofthemodelandhowdothey
affectperformanceandgeneralization? (AppendixSectionD.4)
Throughoutthissectionwewillcomparetotwobaselinestateoftheartarchitectures, Gato(Reed
etal.,2022)andBC-Z(Jangetal.,2021).Importantlybothofthesearetrainedonourdatadescribed
in detail in Sec. 5.2 (which is an important part of our system) since the original models in these
publicationswouldnotexhibitgeneralizationpropertiesrequiredforourevaluationtasks. Gatois,
similarly to RT-1, based on a Transformer architecture, but varies from RT-1 in multiple aspects.
First,itcomputesimagetokenswithoutthenotionoflanguageandeachimagetokenembeddingis
computed separately for each image patch, as opposed to early language fusion and global image
embedding in our model. Second, it does not use a pre-trained text embedding to encode the lan-
guagestring. Italsodoesnotincludeinferencetimeconsiderationsthatarenecessaryforrealrobots
asdiscussedinSec.5.1suchasTokenLearnerandtheremovalofauto-regressiveactions.Inorderto
runGatoonrealrobotsatahighenoughfrequency,wealsolimitthesizeofthemodelcomparedto
theoriginalpublication,whichwas1.2Bparameters(resultinginonrobotinferencetimeof1.9s),
to be of similar size to RT-1 (37M parameters for Gato vs. 35M for RT-1). BC-Z is based on a
ResNetarchitecture,andwasusedinSayCan(Ahnetal.,2022). BC-ZdiffersfromRT-1inthatitis
afeedforwardmodelthatdoesnotuseprevioustimesteps,anditusescontinuousactionsratherthan
discrete action tokens. In addition to the original BC-Z model size, we also compare our method
toalargerversionofBC-ZthathasasimilarnumberofparameterstoRT-1andrefertoitasBC-Z
XL. We study and analyze how each of these design decisions changes performance in Appendix
SectionsD.4andD.5.
Weevaluatethesuccessrateinexperimentstomeasureperformanceontraininginstructions, gen-
eralization to unseen instructions, robustness to backgrounds and distractors, and performance in
long-horizon scenarios, as detailed below. Throughout this section, we evaluate our approach and
baselines with over 3000 real-world trials, making one of the largest scale evaluation of a robot
learningsystemto-date.
6.1 EXPERIMENTALSETUP
As mentioned in Section 4, we evaluate RT-1 with a set of mobile manipulators from Everyday
Robotsinthreeenvironments:tworealofficekitchensandatrainingenvironmentmodelledoffthese
realkitchens. Thetrainingenvironment, showninFig.2(a), consistsofpartialcounterswhilethe
tworealenvironments,showninFig.2(b,c),havesimilarcountertopstothetrainingenvironment,
butvaryinlighting,background,andfullkitchengeometry(e.g.,theremaybeacabinetinsteadof
a drawer or a sink may be visible). The policies are evaluated for performance on training tasks
as well as generalization to new tasks, robustness to unseen environments, and performance when
chainedtogetherforlong-horizontasks,asdetailedbelow.
Seentaskperformance.Toevaluateperformanceonseeninstructions,weevaluateperformanceon
instructionssampledfromthetrainingset. Note,however,thatthisevaluationstillinvolvesvarying
theplacementofobjectsandotherfactorsofthesetup(e.g.,timeofday,robotposition),requiring
the skills to generalize to realistic variability in the environment. In all, we test over 200 tasks in
thisevaluation: 36forpickingobjects,35forknockingobjects,35forplacingthingsupright,48for
movingobjects,18foropeningandclosingvariousdrawers,and36forpickingoutofandplacing
objectsintodrawers.
Unseentasksgeneralization. Toevaluategeneralizationtounseentasks,wetest21novel,unseen
instructions. These instructions are distributed across skills and objects. This ensures that at least
8

--- Page 9 ---
Preprint
someinstancesofeachobjectandskillwerepresentinthetrainingsetbuttheywillbecombinedin
novelways. Forexample,if“pickuptheapple”isheldout,thenthereareothertraininginstructions
thatincludetheapple. ThelistofallunseeninstructionscanbefoundintheAppendixD.1.
Robustness. Toevaluaterobustness, weperform 30real-worldtasksfordistractorrobustnessand
22 tasks for background robustness. The background robustness was tested by evaluating in new
kitchens(whichhavedifferentlightingandbackgroundvisuals)andwithdifferentcountersurfaces
(e.g., a patterned table cloth). Example configurations of the robustness evaluation scenarios are
depictedinFig.4.
Long-horizonscenarios. Wealsoevaluategeneralizationtomorerealisticlong-horizonscenarios,
whicheachrequireexecutingasequenceofskills.Thegoalofthisevaluationistocombinemultiple
generalization axes such as new tasks, objects, environments and test the overall generalization
capabilitiesinrealisticsettings.Theseevaluationsconsistof15long-horizoninstructionsintworeal
kitchens, which require executing sequences of skills consisting of ∼ 10 distinct steps, with each
stepofroughlycomparablescopeasthetraininginstructions.Thesestepsareobtainedautomatically
fromhigherlevelinstructions,suchas“howwouldyouthrowawayalltheitemsonthetable?” by
usingtheSayCansystem(Ahnetal.,2022),asdescribedindetailinSection6.4andAppendixD.3.
Figure 4: Evaluation scenarios for distractors (first row), from left to right: easy (0-5 distractors),
medium (9 distractors), hard (9 distractors and occluded object); background (second row), from
lefttoright: originalenvironment,patternedtablecloth,newkitchen;andrealisticscenariosinthe
realkitchen(thirdrow),generalizationlevelsfromlefttoright: L1,L2andL3.
6.2 CANRT-1LEARNTOPERFORMALARGENUMBEROFINSTRUCTIONS,ANDTO
GENERALIZETONEWTASKS,OBJECTSANDENVIRONMENTS?
To answer our first question, we analyze the overall performance, generalization, and robustness
capabilities of RT-1 compared to previously proposed models. Specifically, we compare to the
model architectures used by Gato (Reed et al., 2022) and BC-Z (Jang et al., 2021), as well as a
largerversionofBC-Z,whichwerefertoasBC-ZXL.Note, however, thatallmodelsaretrained
on the same data as RT-1, and the evaluation only compares the model architectures, not the task
sets,datasets,oroverallroboticsystems. ThecapabilitiesofRT-1aredeterminedtoalargeextent
by the dataset and task set, which we believe improves significantly over prior works (e.g. BC-Z
uses100tasksandtheoriginalGatomodeltrainsastackingtaskwithvariousshapes),andthusthis
comparison should be viewed as rather favorable to the prior models, which also benefit from the
largeanddiversedatasetandtasksetthatwecollected.
The results are shown in Table 2. Across each category, we find that RT-1 outperforms the prior
models significantly. On seen tasks, RT-1 is able to perform 97% of the more than 200 instruc-
9

--- Page 10 ---
Preprint
Model SeenTasks UnseenTasks Distractors Backgrounds
Gato(Reedetal.,2022) 65 52 43 35
BC-Z(Jangetal.,2021) 72 19 47 41
BC-ZXL 56 43 23 35
RT-1(ours) 97 76 83 59
Table 2: Overall performance of RT-1 and baselines across seen tasks, generalization to unseen
tasks,androbustnesstodistractorsandbackgrounds.
tionssuccessfully,whichis25%morethanBC-Zand32%morethanGato. Onunseentasks,RT-1
showsitiscapableofgeneralizingtonovelinstructions,performing76%ofthenever-before-seen
instructions,24%morethanthenextbestbaseline. Whilesuchgeneralizationtonovelinstructions
ismadepossibleduetonaturallanguageconditioningofthepolicy, asthepolicyisabletounder-
stand new combinations of previously seen concepts, all of the baselines are also conditioned on
naturallanguageandinprincipleenjoythesamebenefits. Wefurtherablatedifferentcomponents
ofRT-1inthenextsectiontobetterunderstandwhataspectsofourmethodcontributethemostto
thisdifference. Ondistractorsandbackgrounds,wefindthatRT-1isquiterobust,successfullyexe-
cuting83%ofthedistractorrobustnesstasksand59%ofthebackgroundrobustnesstasks(36%and
18%higherthanthenextbestalternative,respectively). Overall,wefindthatRT-1hashighgeneral
performance,whileexhibitingimpressivedegreesofgeneralizationandrobustness. Weshowexam-
pletrajectoriesoftheRT-1agentincludinginstructionsthatcoverdifferentskills,environmentsand
objectsinFig.5. Wealsopresentadditionaltrajectoryexamplesfordifferentgeneralizationtestsin
theAppendix,whichincludebackgrounds(Fig.10),anddistractors(Fig.12).
Generalization to realistic instructions. Next, we test whether our method generalizes enough
across all the different axes that we evaluated previously to be deployed in a real kitchen, which
poses multiple distribution shifts all at once such as new tasks combinations, object distractors as
wellasanovelenvironment.
To evaluate our algorithm in realistic scenarios in a real kitchen, we construct task sequences to
accomplish a number of realistic goals. The robot restocks several snacks in drawers, tidies up
knocked over condiment bottles and closes drawers left open by humans, prepares a snack with
an orange and a napkin and fetches lost sunglasses and an octopus toy from several places in the
kitchen. The detailed instructions used in these scenarios are listed in the Appendix D.1. The
officekitcheninvolvesadramaticshiftfromthetrainingenvironmentandwecategorizetasksacross
thesescenarioswithvaryinglevelsofgeneralization: L1forgeneralizationtothenewcounter-top
layout and lighting conditions, L2 for additionally generalization to unseen distractor objects, L3
foradditionalgeneralizationtodrasticallynewtasksettings, newtaskobjectsorobjectsinunseen
locations such as near a sink. The three levels that correspond to the three tasks of restocking,
preparingasnackandfetchingalostobjectintherealkitchenaredepictedinthelastrowofFig.4.
ExampletrajectoriesfordifferentlevelsarepresentedintheAppendixinFig.11.
Wereporttheper-tasksuccessrateintheserealisticscenariosalongwiththevaryinggeneralization
levelsinTable3andfindRT-1tobethemostrobustonalllevels. Gatogeneralizesfairlywellatthe
first level but it performs significantly drops for the more difficult generalization scenarios. BC-Z
anditsXLequivalentperformfairlywellatL2levelandbetterthanGatoatL3buttheyarestillnot
atthegeneralizationlevelofRT-1.
6.3 CANWEPUSHTHERESULTINGMODELFURTHERBYINCORPORATINGHETEROGENEOUS
DATASOURCESSUCHASSIMULATIONORDATAFROMDIFFERENTROBOTS?
Next,weexplorethelimitsofRT-1forutilizinghighlyheterogeneousdata.WedemonstratehowRT-
1canincorporateandlearnfromvastlydifferentdatasourcesandimprovefromsuchdatawithout
sacrificingitsoriginal-tasksperformanceacrossthevariedtasksinherentinthisdata.Tothisend,we
conducttwoexperiments: (1)RT-1trainedandtestedonbothrealdataandsimulationdataand(2)
10

--- Page 11 ---
Preprint
“pick water bottle
from the bottom
drawer and put it
on the counter”
“move sponge to
green jalapeno
chips”
“place red bull
can in middle
drawer”
“pull napkin out
of dispenser”
“place coke can
upright”
“open top
drawer”
“pick apple from
bowl”
Figure5: ExampleevaluationtrajectoriesforRT-1acrossvariousinstructions.
GeneralizationScenarioLevels
Models All L1 L2 L3
GatoReedetal.(2022) 30 63 25 0
BC-ZJangetal.(2021) 45 38 50 50
BC-ZXL 55 63 75 38
RT-1(ours) 70 88 75 50
Table 3: Realistic generalization scenarios: we compare model success rate in a realistic Google kitchen
scenariosacrossthreelevelsofgeneralization:L1forgeneralizationtothenewcounter-toplayoutandlighting
conditions,L2foradditionallygeneralizationtounseendistractorobjects,L3foradditionallygeneralization
todrasticallynewtasksettings,newtaskobjectsorinunseenlocationslikenearasink.
RT-1trainedacrosslargedatasetsofdifferenttasks, originallycollectedbydifferentrobots. More
informationoneachisprovidedinAppendixD.2.
Absorbingsimulationdata. Table4showstheabilityofRT-1, andbaselines,toabsorbbothreal
andsimulationdata. Totestthis,wetakealloftherealdemonstrationdatabutwealsoprovidead-
11

--- Page 12 ---
Preprint
60%
50%
RealObjects SimObjects(notseeninreal)
40%
SeenSkill SeenSkill UnseenSkill
Models TrainingData w/Objects w/Objects w/Objects 30%
RT-1 RealOnly 92 23 7 20%
RT-1 Real+Sim 90(-2) 87(+64) 33(+26)
10%
0%
Sim-seen Objects Sim-seen Objects Real Tasks
w/ Skills w/o Skills
ot
derapmoC
etaR
sseccuS
ylno
laeR
Real +Sim Data
+64%
+26%
-2%
Table 4: Experimental results for incorporating simulation data in RT-1. Adding simulation data
doesnotimpacttheperformanceonrealobjects,whilesignificantlyimprovingrealperformanceon
objectsthatwereonlyintroducedinsimulation(+64%). Italsoimprovesreal-worldgeneralization
onsimulatedobjectsusedwithskillsseenonlyintherealworld(+26%),e.g. “moveXtoY”where
Xonlyappearedinsimulated“pickX”task.
ditionalsimulationdatathatincludesobjectsthattherobothasneverseenintherealworld. Specifi-
cally,wespecifydifferentgeneralizationscenarios: forseenskillswithrealobjectsthetrainingdata
hasrealdataofthatinstruction(i.e.,performanceonseentasks),forseenskillswithsimobjectsthe
trainingdatahassimdataofthatinstruction(e.g. “pickupasimobject”,whichwaspresentinsim),
andforunseenskillswithsimobjectsthetrainingdatahassimdataofthatobjectbutthereareno
examplesoftheinstructiondescribingtheskillwiththatobjecteitherinsimorinreal(e.g.,“move
asimobjecttoapple”,eventhoughtherobothasonlypracticedinpickingthatsimobjectandnot
movingitnearotherobjects). Allevaluationsaredoneintherealworldbuttolimitthenumberof
instructionsevaluated,wefocusonpickandmove-toskills.
We find in Table 4 that for RT-1, we do not lose performance adding simulation data compared
to the Real Only dataset. We do however, see a significant increase in performance (from 23% to
87%)onobjectsandtasksseenonlyinsimulation, toapproximatelytheperformanceofthethose
in real, demonstrating an impressive degree of domain transfer. We also see a significant increase
inperformanceonunseeninstructionsfrom7%to33%;impressivegiventheobjectinquestionhas
never been seen in real and the instruction never seen at all. Overall, we find that RT-1 is able to
efficientlyabsorbnewdata,evenfromaverydifferentdomain.
Absorbing data from different robots. To push the data absorption limits of RT-1, we conduct
an additional set of experiments where we combine two data sources that originate from different
robots: Kuka IIWA as well as the Everyday Robots mobile manipulators used in the experiments
sofar. TheKukadatacontainsallthesuccessfulexamplescollectedinQT-Opt(Kalashnikovetal.,
2018),whichcorrespondsto209kepisodes,wheretherobotwasindiscriminatelygraspingobjects
inabin(seeanexampleofaKukaepisodeinTable.5). TotestwhetherRT-1caneffectivelyabsorb
thesetwoverydifferentdatasets,whichwerefertoasthestandard“Classroomeval”,aswellasthe
performance on the newly constructed tasks that reflect the bin-picking setup present in the Kuka
data,whichwerefertoasthe“Bin-pickingeval”(seeFig.6).
Wewouldliketoemphasizethedifficultyofthissettingbynotingthemajordifferencesbetweenthe
datasets. Notonlyaretherobotsthatcollectedthedatadifferentinappearanceandactionspace,but
alsotheenvironmenttheyweredeployedinhasdifferentappearanceanddynamics. Inadditionthe
QT-Optdatapresentsacompletelydifferentactiondistribution–itwascollectedbyanRLagentas
opposedtohumandemonstrationspresentinourdataset.
The results are presented in Table 5. We observe that the model that mixes the RT-1 data and the
Kukadatahasonlyaminimaldecreaseintheoriginaltasks’performance(i.e. Classroomeval),i.e.
2%. Even more importantly, in the Bin-picking eval, we observe that the model trained on multi-
robotdataperformsat39%comparedtothe22%ofthemodelthatwastrainedonlyontheRT-1data.
Thisisa17%performancedifference(almost2x). Additionally,RT-1trainedonKukabin-picking
data and evaluated on the bin-picking tasks with the Everyday Robots (EDR) robot achieves 0%
performance, confirming that it is difficult to transfer a behavior from another robot morphology.
However, mixing the data from both robots allows RT-1 to infer the correct actions of the EDR
12

--- Page 13 ---
Preprint
Figure6: InTable5,RT-1istrainedwithdatafromtworoboticsplatformsandlearnstogeneralize
acrossthem.
17.5%
15.0%
12.5% Models TrainingData Classroomeval Bin-pickingeval
10.0%
RT-1 Kukabin-pickingdata+EDRdata 90(-2) 39(+17)
7.5%
RT-1 EDRonlydata 92 22
5.0% RT-1 Kukabin-pickingonlydata 0 0
2.5%
0.0%
2.5%
Bin-picking Eval Classroom Eval
ylnO
RDE
ot
derapmoC
etaR
sseccuS
EDR +Kuka Data
+17%
-2%
Table 5: Experimental results for mixing data from two different robots. Incorporating Kuka bin-
pickingdatafromQT-Opt(Kalashnikovetal.,2018)inRT-1minimallyimpactsthestandardclass-
roomevaluationperformanceandresultsinalmosta2ximprovementingeneralizationtotheBin-
pickingevaluation(thatissimilartothesetupintheKukadata)ontheEverydayRobotsmanipulator.
Thisdemonstratesaneffectivetransferacrosstwodifferentrobotmorphologies.
robot even when faced with the states observed by Kuka robots. This is achieved without explicit
demonstrationsofbin-pickingonEDRrobotandbytakingadvantageofpastexperiencescollected
byKukarobots. TheseresultsindicatethatRT-1’sabsorptionpropertiesalsoincludetheabilityto
acquire new skills through observing other robots’ experiences and present an exciting avenue of
futureworkwherewecombinemanymoremulti-robotdatasetstoenhancetherobotcapabilities.
6.4 HOWDOVARIOUSMETHODSGENERALIZELONG-HORIZONROBOTICSCENARIOS?
In the next set of experiments we evaluate whether our method generalizes enough to be used in
long-horizonrealistickitchensettings. Toanswerthisquestion,weexecuteRT-1andvariousbase-
lineswithintheSayCan(Ahnetal.,2022)frameworkintwodifferentrealkitchens. SinceSayCan
combines many low-level instructions to perform high-level instructions, the number of possible
high-level instructions increases combinatorially with skills, so the skill-breadth of RT-1 can be
fullyseen(formoredetailsontheSayCanalgorithmpleaserefertoAhnetal.(2022)). Thesuccess
rateoflong-horizontasksalsodecreasesexponentiallywiththelengthofthetask,sohighsuccess
rates in manipulation skills are particularly important. Furthermore, as mobile manipulation tasks
requirebothnavigationandmanipulation,thepoliciesabilitytoberobusttobasepositioniscrucial.
MoredetailisprovidedinAppendixD.3.
Table 6 shows our results (on instructions in Appendix Table 12). Except for original SayCan, all
methodsget87%asplanningsuccessrate,andRT-1performsthebest,with67%executionsuccess
rate in Kitchen1. Kitchen2 constitutes a much more challenging generalization scene, since the
Robot Classroom training scenes are modeled after Kitchen1 (see the pictures of the kitchens in
Fig.2). Duetothisgeneralizationdifficulty,SayCanwithGatoisnotabletofinishanylonghorizon
task, andSayCanwith BC-Zisabletoachieve asuccessrateof13%. TheoriginalSayCan paper
didnotevaluateperformanceinanewkitchen. Surprisingly,themanipulationperformancedoesnot
13

--- Page 14 ---
Preprint
seeavisibledropfromKitchen1toKitchen2forourmethod. Inthesupplementaryvideo,weshow
thatthisenablesustooperateunseendrawersinKitchen2,andthatwecanuseSayCan-RT1toplan
andexecuteultra-longhorizontasks,withasmanyas50steps.
SayCantasksinKitchen1 SayCantasksinKitchen2
Planning Execution Planning Execution
OriginalSayCan(Ahnetal.,2022)∗ 73 47 - -
SayCanw/Gato(Reedetal.,2022) 87 33 87 0
SayCanw/BC-Z(Jangetal.,2021) 87 53 87 13
SayCanw/RT-1(ours) 87 67 87 67
Table6: SayCanstylelonghorizontasksinKitchen1andKitchen2. (*OriginalSayCanevalusesa
slightlydifferentpromptsotheplanningsuccessrateislower.)
6.5 HOWDOGENERALIZATIONMETRICSCHANGEWITHVARYINGAMOUNTSOFDATA
QUANTITYANDDATADIVERSITY?
While previous works have shown the scaling abilities of Transformer-based models (Lee et al.,
2022a;Reedetal.,2022;Jiangetal.,2022)withthenumberofmodelparameters,inmanyrobotics
works the model size is often not the primary bottleneck, and the maximum size is limited by the
latency requirement for running such models on real robots. Instead, in this study we focus on
ablatingtheinfluenceofdatasetsizeanddiversity,astheyplayanimportantroleinthetraditionally
data-limited robot learning field. Since data collection is particularly expensive for real robots, it
is important to quantify what kind of data our models need to achieve a certain performance and
generalization. Thus,ourlastquestionfocusesonthescalingpropertiesofRT-1withdifferentdata
properties.
Generalization
Models %Tasks %Data SeenTasks All UnseenTasks Distractors Backgrounds
SmallerData
RT-1(ours) 100 100 97 73 76 83 59
RT-1 100 51 71 50 52 39 59
RT-1 100 37 55 46 57 35 47
RT-1 100 22 59 29 14 31 41
NarrowerData
RT-1(ours) 100 100 97 73 76 83 59
RT-1 75 97 86 54 67 42 53
Table 7: Various data ablations of RT-1 across seen tasks, generalization to unseen tasks, and ro-
bustnesstodistractorsandbackgrounds. Datadiversityhasahigherimpactontheperformanceand
generalizationthandataquantity.
In Table 7 we show the performance, generalization, and robustness of RT-1 as we decrease the
dataset size (% data) and the dataset diversity (% tasks). To separate the axes of dataset size and
diversity, we create smaller datasets with the same task diversity by removing data from the tasks
withthelargestdata,cappingthenumberofexamplespertaskat200(resultingin51%ofthedata),
14

--- Page 15 ---
Preprint
100(37%ofthedata),and50(22.5%ofthedata). Tocreateanarrowdataset,weremovethetasks
withtheleastdata,thuskeeping97%oftheoveralldatabutonly75%ofthetasks. Aswedecrease
dataset size, we see a general trend of decreasing performance and a steeper trend of decreasing
generalization. Aswemakethedatasetmorenarrow,weseemuchsteeperperformancereductions,
particularlyintermsofgeneralization. Infact,removing25%ofthetaskswhilekeeping97%ofthe
dataachievesanequivalentgeneralizationperformancetoreducingthedatasetsizebyasmuchas
49%. Ourkeytakeawayisthusthatdatadiversityismoreessentialthandataquantity.
7 CONCLUSIONS, LIMITATIONS AND FUTURE WORK
We presented Robotics Transformer 1, RT-1, a robot learning method that can effectively absorb
largeamountsofdataandscaleswithdataquantityanddiversity. WetrainedRT-1onalargedataset
of demonstrations containing over 130k episodes collected over the course of 17 months with 13
robots. Inourbroadsetofexperiments,wedemonstratedthatourmethodthatcanperformover700
instructionsat97%successrateandeffectivelygeneralizetonewtasks, objectsandenvironments
betterthanpreviouslypublishedbaselines. WealsodemonstratedthatRT-1cansuccessfullyabsorb
heterogeneousdatafromsimulationandotherrobotmorphologieswithoutsacrificingoriginal-tasks
performanceandwhileimprovinggeneralizationtonewscenarios.Lastly,weshowedhowthislevel
ofperformanceandgeneralizationallowedustoexecuteverylong-horizontasksintheSayCan(Ahn
etal.,2022)framework,withasmanyas50steps.
While RT-1 presents a promising step towards large-scale robot learning with an data-absorbent
model, it comes with a number of limitations. First, it is an imitation learning method, which
inheritsthechallengesofthatclassofapproachessuchasthefactthatitmaynotbeabletosurpass
theperformanceofthedemonstrators. Second, thegeneralizationtonewinstructionsislimitedto
thecombinationsofpreviouslyseenconceptsandRT-1isnotyetabletogeneralizetoacompletely
newmotionthathasnotbeenseenbefore. Lastly, ourmethodispresentedonalargebutnotvery
dexteroussetofmanipulationtasks. WeplantocontinueextendingthesetofinstructionsthatRT-1
enablesandgeneralizestotoaddressthischallenge.
Asweexplorefuturedirectionsforthiswork,wehopetoscalethenumberofrobotskillsfasterby
developingmethodsthatallownon-expertstotraintherobotviadirecteddatacollectionandmodel
prompting. While the current version of RT-1 is fairly robust especially to distractor objects, its
robustness to backgrounds and environments could be further improved by greatly increasing the
environmentdiversity. WealsohopetoimprovethereactionspeedsandcontextretentionofRT-1
throughscalableattentionandmemory.
Toallowtheresearchcommunitytobuildontopofthiswork,wehaveopen-sourcedthecodeforRT-
14,whichwehopewillprovideresearcherswithavaluableresourceforfutureresearchforscaling
uprobotlearning.
ACKNOWLEDGMENTS
We would like to acknowledge Aleksandra Faust, Andy Christiansen, Chuyuan Fu, Daniel Kap-
pler,DavidRendleman,EricJang,JessicaGomez,JessicaLin,JieTan,JoshWeaver,JustinBoyd,
KrzysztofChoromanski,MatthewBennice,MengyuanYan,MrinalKalakrishnan,NikStewart,Paul
Wohlhart, Peter Pastor, Pierre Sermanet, Wenlong Lu, Zhen Yu Song, Zhuo Xu, and the greater
teamsatRoboticsatGoogleandEverydayRobotsfortheirfeedbackandcontributions.
REFERENCES
MichaelAhn,AnthonyBrohan,NoahBrown,YevgenChebotar,OmarCortes,ByronDavid,Chelsea
Finn,KeerthanaGopalakrishnan,KarolHausman,AlexHerzog,etal. DoasIcan,notasIsay:
Groundinglanguageinroboticaffordances. arXivpreprintarXiv:2204.01691,2022.
DanielCer,YinfeiYang,Sheng-yiKong,NanHua,NicoleLimtiaco,RhomniStJohn,NoahCon-
stant,MarioGuajardo-Cespedes,SteveYuan,ChrisTar,etal. Universalsentenceencoder. arXiv
preprintarXiv:1803.11175,2018.
4http://github.com/google-research/robotics_transformer
15

--- Page 16 ---
Preprint
LiliChen,KevinLu,AravindRajeswaran,KiminLee,AdityaGrover,MishaLaskin,PieterAbbeel,
AravindSrinivas,andIgorMordatch.Decisiontransformer:Reinforcementlearningviasequence
modeling. Advancesinneuralinformationprocessingsystems,34:15084–15097,2021.
MichaelJae-YoonChung,AbramLFriesen,DieterFox,AndrewNMeltzoff,andRajeshPNRao.
Abayesiandevelopmentalapproachtoroboticgoal-basedimitationlearning. PloSone,10(11):
e0141965,2015.
Sudeep Dasari, Frederik Ebert, Stephen Tian, Suraj Nair, Bernadette Bucher, Karl Schmeckpeper,
Siddharth Singh, Sergey Levine, and Chelsea Finn. Robonet: Large-scale multi-robot learning.
InConferenceonRobotLearning,2019.
Marc Peter Deisenroth, Peter Englert, Jan Peters, and Dieter Fox. Multi-task policy search for
robotics. In2014IEEEinternationalconferenceonroboticsandautomation(ICRA),pp.3876–
3881.IEEE,2014.
ColineDevin, AbhishekGupta, TrevorDarrell, PieterAbbeel, andSergeyLevine. Learningmod-
ularneuralnetworkpoliciesformulti-taskandmulti-robottransfer. In2017IEEEinternational
conferenceonroboticsandautomation(ICRA),pp.2169–2176.IEEE,2017.
MiroslavDud´ık,JohnLangford,andLihongLi.Doublyrobustpolicyevaluationandlearning.arXiv
preprintarXiv:1103.4601,2011.
Frederik Ebert, Yanlai Yang, Karl Schmeckpeper, Bernadette Bucher, Georgios Georgakis, Kostas
Daniilidis, Chelsea Finn, and Sergey Levine. Bridge data: Boosting generalization of robotic
skillswithcross-domaindatasets. arXivpreprintarXiv:2109.13396,2021.
Kuan Fang, Alexander Toshev, Li Fei-Fei, and Silvio Savarese. Scene memory transformer for
embodiedagentsinlong-horizontasks.InProceedingsoftheIEEE/CVFConferenceonComputer
VisionandPatternRecognition,pp.538–547,2019.
RoyFox,RonBerenstein,IonStoica,andKenGoldberg. Multi-taskhierarchicalimitationlearning
forhomeautomation. In2019IEEE15thInternationalConferenceonAutomationScienceand
Engineering(CASE),pp.1–8.IEEE,2019.
Abhinav Gupta, Adithyavairavan Murali, Dhiraj Prakashchand Gandhi, and Lerrel Pinto. Robot
learninginhomes:Improvinggeneralizationandreducingdatasetbias. Advancesinneuralinfor-
mationprocessingsystems,31,2018.
AgrimGupta,LinxiFan,SuryaGanguli,andLiFei-Fei.Metamorph:Learninguniversalcontrollers
withtransformers. arXivpreprintarXiv:2203.11931,2022.
JosiahPHanna,PeterStone,andScottNiekum. Bootstrappingwithmodels: Confidenceintervals
foroff-policyevaluation. InThirty-FirstAAAIConferenceonArtificialIntelligence,2017.
Daniel Ho, Kanishka Rao, Zhuo Xu, Eric Jang, Mohi Khansari, and Yunfei Bai. RetinaGAN:
An object-aware approach to sim-to-real transfer, 2020. URL https://arxiv.org/abs/
2011.03148.
De-An Huang, Yu-Wei Chao, Chris Paxton, Xinke Deng, Li Fei-Fei, Juan Carlos Niebles, Ani-
meshGarg, andDieterFox. Motionreasoningforgoal-basedimitationlearning. In2020IEEE
InternationalConferenceonRoboticsandAutomation(ICRA),pp.4878–4884.IEEE,2020.
Alexander Irpan, Kanishka Rao, Konstantinos Bousmalis, Chris Harris, Julian Ibarz, and Sergey
Levine. Off-policyevaluationviaoff-policyclassification. AdvancesinNeuralInformationPro-
cessingSystems,32,2019.
Stephen James, Zicong Ma, David Rovick Arrojo, and Andrew J Davison. RLBench: The robot
learningbenchmark&learningenvironment. IEEERoboticsandAutomationLetters,5(2):3019–
3026,2020.
EricJang,AlexIrpan,MohiKhansari,DanielKappler,FrederikEbert,CoreyLynch,SergeyLevine,
andChelseaFinn. Bc-z: Zero-shottaskgeneralizationwithroboticimitationlearning. InConfer-
enceonRobotLearning,pp.991–1002.PMLR,2021.
16

--- Page 17 ---
Preprint
MichaelJanner,QiyangLi,andSergeyLevine. Reinforcementlearningasonebigsequencemod-
elingproblem. InICML2021WorkshoponUnsupervisedReinforcementLearning,2021.
YunfanJiang,AgrimGupta,ZichenZhang,GuanzhiWang,YongqiangDou,YanjunChen,LiFei-
Fei, Anima Anandkumar, Yuke Zhu, and Linxi Fan. Vima: General robot manipulation with
multimodalprompts. arXivpreprintarXiv:2210.03094,2022.
TomJurgenson,OrAvner,EdwardGroshev,andAvivTamar. Sub-goaltreesaframeworkforgoal-
basedreinforcementlearning.InInternationalConferenceonMachineLearning,pp.5020–5030.
PMLR,2020.
Dmitry Kalashnikov, Alex Irpan, Peter Pastor, Julian Ibarz, Alexander Herzog, Eric Jang, Deirdre
Quillen, Ethan Holly, Mrinal Kalakrishnan, Vincent Vanhoucke, et al. Scalable deep reinforce-
mentlearningforvision-basedroboticmanipulation. InConferenceonRobotLearning,pp.651–
673.PMLR,2018.
Dmitry Kalashnikov, Jacob Varley, Yevgen Chebotar, Benjamin Swanson, Rico Jonschkowski,
Chelsea Finn, Sergey Levine, and Karol Hausman. Mt-opt: Continuous multi-task robotic re-
inforcementlearningatscale. arXivpreprintarXiv:2104.08212,2021a.
Dmitry Kalashnikov, Jake Varley, Yevgen Chebotar, Ben Swanson, Rico Jonschkowski, Chelsea
Finn,SergeyLevine,andKarolHausman. MT-opt: Continuousmulti-taskroboticreinforcement
learningatscale. arXiv,2021b.
ThomasKollar,StefanieTellex,DebRoy,andNicholasRoy.Towardunderstandingnaturallanguage
directions. In20105thACM/IEEEInternationalConferenceonHuman-RobotInteraction(HRI),
pp.259–266.IEEE,2010.
Kuang-Huei Lee, Ofir Nachum, Mengjiao Yang, Lisa Lee, Daniel Freeman, Winnie Xu, Sergio
Guadarrama,IanFischer,EricJang,HenrykMichalewski,etal. Multi-gamedecisiontransform-
ers. arXivpreprintarXiv:2205.15241,2022a.
Kuang-Huei Lee, Ted Xiao, Adrian Li, Paul Wohlhart, Ian Fischer, and Yao Lu. PI-QT-Opt: Pre-
dictive information improves multi-task robotic reinforcement learning at scale. arXiv preprint
arXiv:2210.08217,2022b.
Ian Lenz, Honglak Lee, and Ashutosh Saxena. Deep learning for detecting robotic grasps. The
InternationalJournalofRoboticsResearch,34(4-5):705–724,2015.
CoreyLynchandPierreSermanet. Languageconditionedimitationlearningoverunstructureddata.
arXivpreprintarXiv:2005.07648,2020.
MattMacMahon,BrianStankiewicz,andBenjaminKuipers. Walkthetalk: Connectinglanguage,
knowledge,andactioninrouteinstructions. Def,2(6):4,2006.
HongyuanMei,MohitBansal,andMatthewRWalter. Listen,attend,andwalk: Neuralmappingof
navigationalinstructionstoactionsequences. InThirtiethAAAIConferenceonArtificialIntelli-
gence,2016.
Suraj Nair, Eric Mitchell, Kevin Chen, Silvio Savarese, Chelsea Finn, et al. Learning language-
conditioned robot behavior from offline data and crowd-sourced annotation. In Conference on
RobotLearning,pp.1303–1315.PMLR,2022.
NikiParmar,AshishVaswani,JakobUszkoreit,LukaszKaiser,NoamShazeer,AlexanderKu,and
Dustin Tran. Image transformer. In International conference on machine learning, pp. 4055–
4064.PMLR,2018.
Alexander Pashevich, Cordelia Schmid, and Chen Sun. Episodic transformer for vision-and-
language navigation. In Proceedings of the IEEE/CVF International Conference on Computer
Vision,pp.15942–15952,2021.
EthanPerez,FlorianStrub,HarmdeVries,VincentDumoulin,andAaronCourville. Film: Visual
reasoning with a general conditioning layer. Proceedings of the AAAI Conference on Artificial
Intelligence, 32(1), Apr. 2018. doi: 10.1609/aaai.v32i1.11671. URL https://ojs.aaai.
org/index.php/AAAI/article/view/11671.
17

--- Page 18 ---
Preprint
LerrelPintoandAbhinavGupta. Supersizingself-supervision:Learningtograspfrom50ktriesand
700robothours. In2016IEEEinternationalconferenceonroboticsandautomation(ICRA),pp.
3406–3413.IEEE,2016.
DeanAPomerleau. Alvinn: Anautonomouslandvehicleinaneuralnetwork. Advancesinneural
informationprocessingsystems,1,1988.
Alec Radford, Jong Wook Kim, Chris Hallacy, Aditya Ramesh, Gabriel Goh, Sandhini Agarwal,
Girish Sastry, Amanda Askell, Pamela Mishkin, Jack Clark, et al. Learning transferable visual
models from natural language supervision. In International Conference on Machine Learning,
pp.8748–8763.PMLR,2021.
AntoninRaffin,AshleyHill,Rene´Traore´,Timothe´eLesort,NataliaD´ıaz-Rodr´ıguez,andDavidFil-
liat. Decouplingfeatureextractionfrompolicylearning:assessingbenefitsofstaterepresentation
learningingoalbasedrobotics. arXivpreprintarXiv:1901.08651,2019.
AdityaRamesh,MikhailPavlov,GabrielGoh,ScottGray,ChelseaVoss,AlecRadford,MarkChen,
andIlyaSutskever. Zero-shottext-to-imagegeneration. InInternationalConferenceonMachine
Learning,pp.8821–8831.PMLR,2021.
Scott Reed, Konrad Zolna, Emilio Parisotto, Sergio Gomez Colmenarejo, Alexander Novikov,
Gabriel Barth-Maron, Mai Gimenez, Yury Sulsky, Jackie Kay, Jost Tobias Springenberg, et al.
Ageneralistagent. arXivpreprintarXiv:2205.06175,2022.
MichaelRyoo, AJPiergiovanni, AnuragArnab, MostafaDehghani, andAneliaAngelova. Token-
learner:Adaptivespace-timetokenizationforvideos.AdvancesinNeuralInformationProcessing
Systems,34:12786–12797,2021.
Ashutosh Saxena, Justin Driemeyer, Justin Kearns, and Andrew Ng. Robotic grasping of novel
objects. Advancesinneuralinformationprocessingsystems,19,2006.
NurMuhammadMahiShafiullah,ZichenJeffCui,AriuntuyaAltanzaya,andLerrelPinto.Behavior
transformers: Cloningkmodeswithonestone. arXivpreprintarXiv:2206.11251,2022.
Pratyusha Sharma, Lekha Mohan, Lerrel Pinto, and Abhinav Gupta. Multiple interactions made
easy(mime): Largescaledemonstrationsdataforimitation. InConferenceonrobotlearning,pp.
906–915.PMLR,2018.
Mohit Shridhar, Lucas Manuelli, and Dieter Fox. Cliport: What and where pathways for robotic
manipulation. InProceedingsofthe5thConferenceonRobotLearning(CoRL),2021.
Mohit Shridhar, Lucas Manuelli, and Dieter Fox. Perceiver-actor: A multi-task transformer for
roboticmanipulation. arXivpreprintarXiv:2209.05451,2022.
AndrewSilva, NinaMoorman, WilliamSilva, ZulfiqarZaidi, NakulGopalan, andMatthewGom-
bolay.Lancon-learn:Learningwithlanguagetoenablegeneralizationinmulti-taskmanipulation.
IEEERoboticsandAutomationLetters,7(2):1635–1642,2021.
Avi Singh, Eric Jang, Alexander Irpan, Daniel Kappler, Murtaza Dalal, Sergey Levinev, Mohi
Khansari, and Chelsea Finn. Scalable multi-task imitation learning with autonomous improve-
ment. In 2020 IEEE International Conference on Robotics and Automation (ICRA), pp. 2167–
2173.IEEE,2020.
Simon Stepputtis, Joseph Campbell, Mariano Phielipp, Stefan Lee, Chitta Baral, and Heni
Ben Amor. Language-conditioned imitation learning for robot manipulation tasks. Advances
inNeuralInformationProcessingSystems,33:13139–13150,2020.
MingxingTanandQuocLe. EfficientNet: Rethinkingmodelscalingforconvolutionalneuralnet-
works. In Kamalika Chaudhuri and Ruslan Salakhutdinov (eds.), Proceedings of the 36th In-
ternational Conference on Machine Learning, volume 97 of Proceedings of Machine Learning
Research, pp. 6105–6114. PMLR, 09–15 Jun 2019. URL https://proceedings.mlr.
press/v97/tan19a.html.
18

--- Page 19 ---
Preprint
Stefanie Tellex, Thomas Kollar, Steven Dickerson, Matthew Walter, Ashis Banerjee, Seth Teller,
andNicholasRoy. Understandingnaturallanguagecommandsforroboticnavigationandmobile
manipulation. InProceedingsoftheAAAIConferenceonArtificialIntelligence,volume25,pp.
1507–1514,2011.
Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N Gomez,
Łukasz Kaiser, and Illia Polosukhin. Attention is all you need. Advances in neural informa-
tionprocessingsystems,30,2017.
UlrichViereck,AndreasPas,KateSaenko,andRobertPlatt. Learningavisuomotorcontrollerfor
realworldroboticgraspingusingsimulateddepthimages. InConferenceonrobotlearning,pp.
291–300.PMLR,2017.
TedXiao,EricJang,DmitryKalashnikov,SergeyLevine,JulianIbarz,KarolHausman,andAlexan-
derHerzog. Thinkingwhilemoving:Deepreinforcementlearningwithconcurrentcontrol. arXiv
preprintarXiv:2004.06089,2020.
TianheYu,DeirdreQuillen,ZhanpengHe,RyanJulian,KarolHausman,ChelseaFinn,andSergey
Levine.Meta-world:Abenchmarkandevaluationformulti-taskandmetareinforcementlearning.
InConferenceonrobotlearning,pp.1094–1100.PMLR,2020.
TianhaoZhang,ZoeMcCarthy,OwenJow,DennisLee,XiChen,KenGoldberg,andPieterAbbeel.
Deep imitation learning for complex manipulation tasks from virtual reality teleoperation. In
2018IEEEInternationalConferenceonRoboticsandAutomation(ICRA),pp.5628–5635.IEEE,
2018.
Yichi Zhang and Joyce Chai. Hierarchical task learning from language instructions with unified
transformersandself-monitoring. arXivpreprintarXiv:2106.03427,2021.
19

--- Page 20 ---
Preprint
APPENDIX
A AUTHOR CONTRIBUTIONS
• Evaluations (ablations, designing procedures, implementations, and running abla-
tions): YevgenChebotar,KeerthanaGopalakrishnan,KarolHausman,JulianIbarz,Brian
Ichter, Alex Irpan, Isabel Leal, Kuang-Huei Lee, Yao Lu, Ofir Nachum, Kanishka Rao,
SumedhSontakke,AustinStone,QuanVuong,FeiXia,TedXiao,andTianheYu.
• Network Architecture (tokenizer, training, inference): Yevgen Chebotar, Keerthana
Gopalakrishnan, Julian Ibarz, Alex Irpan, Kuang-Huei Lee, Yao Lu, Karl Pertsch, Kan-
ishkaRao,MichaelRyoo,SumedhSontakke,AustinStone,andQuanVuong.
• DevelopedInfrastructure(data,training,collect,simulation,evaluations,storage,and
operations): AnthonyBrohan,KeerthanaGopalakrishnan,KarolHausman,AlexHerzog,
JasmineHsu,AlexIrpan,NikhilJoshi,RyanJulian,DmitryKalashnikov,YuhengKuang,
IsabelLeal,YaoLu,FeiXia,TedXiao,PengXu,SichunXu,andTianheYu.
• Leadership(managedoradvisedontheproject): ChelseaFinn,KarolHausman,Julian
Ibarz,SallyJesmonth,SergeyLevine,YaoLu,IgorMordatch,CarolinaParada,Kanishka
Rao,PannagSanketi,VincentVanhoucke.
• Paper (figures, vizualizations, writing): Keerthana Gopalakrishnan, Karol Hausman,
BrianIchter,SergeyLevine,OfirNachum,KarlPertsch,KanishkaRao,AustinStone,Fei
Xia,andTedXiao.
• Data collection and evaluations: Noah Brown, Justice Carbajal, Joseph Dabis, Tomas
Jackson,UtsavMalla,DeekshaManjunath,JodilyPeralta,EmilyPerez,JornellQuiambao,
Grecia Salazar, Kevin Sayed, Jaspiar Singh, Clayton Tan, Huong Tran, Steve Vega, and
BriannaZitkovich.
B MODEL CARD
WepresenttheModelCardforRT-1inFig.7.
C MODEL AND DATA
C.1 MODELINFERENCE
In addition to the inference speed requirement, we need to ensure that our system outputs actions
at a consistent frequency, avoiding jitter. To accomplish this, we introduce a fixed-time waiting
mechanismthatwaitsacertainamountoftime(280ms,themaxobservedlatencyofallcomponents)
afterthestate,thatwasusedtocomputethenextaction,hasbeencaptured,butbeforeapplyingthe
action,similarlytotheproceduredescribedbyXiaoetal.(2020).
C.2 DATACOLLECTIONATSCALE.
Each of the robots autonomously approaches its station at the beginning of the episode and com-
municates to the operator the instruction that they should demonstrate to the robot. To ensure a
balanced dataset as well as randomization of the scene, we created a software module responsible
for sampling the instructions to be demonstrated as well as the randomization of the background
configuration. Each of the robots tells the demonstrator how to randomize the scene and which
instructiontodemonstrate.
Demonstrations are collected with direct line-of-sight between operator and robot using 2 virtual
reality remotes. We map remote controls onto our policy action space to preserve consistency of
thetransition-dynamics. 3Dpositionandrotationaldisplacementsoftheremotearemappedto6d
displacementsoftherobottool. Thex,ypositionofthejoystickismappedtoaturningangleand
drivingdistanceofthemobilebase. Wecomputeandtracktrajectoriestothetargetposesthatwe
obtainfromthejoystickcommands.
20

--- Page 21 ---
Preprint
ModelCardforRT-1(RoboticsTransformer)
ModelDetails
• DevelopedbyresearchersatRoboticsatGoogleandEverydayRobots,2022,v1.
• Transformer-basedmodel,builtuponaFiLM-conditionedEfficientNet(Tan&Le,
2019),aTokenLearner(Ryooetal.,2021),andaTransformer(Vaswanietal.,2017).
• Trainedwithimitationlearningwithinputsofnaturallanguagetasksandimagesand
outputrobotactions.
IntendedUse
• IntendedtobeusedforcontrollinganEverydayRobotformanipulationtasks.
• Unclearsuitabilityasalearnedrepresentationfordifferentroboticembodiments,
environments,orsignificantlyvarieddownstreamtasks.
• Notsuitableforinteractionwithhumans.
Factors
• Factorsincludevaryingbackgrounds,lighting,scenes,baseposition,andnovel
naturallanguagetasks. Hardwarefactorsincludecameraandrobotembodiment.
Metrics
• Evaluationmetricsincludeseentaskperformance,unseentaskperformance,
robustnesstobackgroundsanddistractors,andperformanceinlong-horizon
scenarios. Eachmeasuresthesuccessrateofthemodelperformingnaturallanguage
specifiedtaskswithrandomizedobjectsandobjectlocationsandvaryingscenes.
TrainingData
• Trainedon130ktele-operationdemonstrationsover13robotsand744tasks.
Skill Count Description ExampleInstruction
PickObject 130 Lifttheobjectoffthesurface pickicedteacan
MoveObjectNearObject 337 Movethefirstobjectnearthesecond movepepsicannearrxbarblueberry
PlaceObjectUpright 8 Placeanelongatedobjectupright placewaterbottleupright
KnockObjectOver 8 Knockanelongatedobjectover knockredbullcanover
Open/CloseDrawer 6 Openorcloseanyofthecabinetdrawers openthetopdrawer
PlaceObjectintoReceptacle 84 Placeanobjectintoareceptacle placebrownchipbagintowhitebowl
PickObjectfromReceptacle 162 Pickanobjectupfromalocationandthen pickgreenjalapenochipbagfrompaper
andPlaceontheCounter placeitonthecounter bowlandplaceoncounter
Additionaltasks 9 Skillstrainedforrealistic,longinstructions pullnapkinoutofdispenser
Total 744
EvaluationData
• Evaluatedonreal-worldrandomizedscenesandover3000totalrolloutsinthe
environmentitwastrainedonaswellastwonewofficekitchenenvironments.
QuantitativeAnalyses
• RT-1showshigh-performanceandrobustnessandcanlearnfromheterogenousdata.
EthicalConsiderations
• Earlyresearch,modelhasnotyetbeenevaluatedforsuitabilitytouseoutsideofits
currentresearchsetting.
CaveatsandRecommendations
• Whilethecurrentmodelcoversonlyasmallportionofpossibleroboticmanipulation
tasks,itpresentsarecipeforscalableroboticlearningandanarchitecturethatshows
favorablegeneralizationanddataabsorptionproperties.
Figure7: ModelCardforRT-1.
21

--- Page 22 ---
Preprint
C.3 MODELSELECTIONATSCALE
Asrobotlearningsystemsbecomemorecapableandthenumberofinstructionstheycanhandlein-
creases,evaluationofthesemodelsbecomesdifficult(Kalashnikovetal.,2021a;Jangetal.,2021).
Thisisanimportantconsiderationnotonlyforevaluatingdifferentmodelclassesanddatadistribu-
tionsduringthedevelopmentprocess,butalsoforselectingthemostperformantmodelcheckpoints
for a particular training run. While there have been a number of proposed solutions to this prob-
lem (Dud´ık et al., 2011; Irpan et al., 2019; Hanna et al., 2017), mostly known in the offline rein-
forcementlearningliteratureas“off-policyevaluation”,itstillremainsanopenresearchchallenge
toevaluatemulti-taskrobotlearningsystemsatscale.
Inthiswork,weproposeleveragingsimulationfor“realtosim”transferasascalabletoolthatpro-
videsanapproximateestimateofmodelperformanceduringtrainingacrossmanyrealtasks.Werun
policiestrainedfromrealdatainasimulatortotestthefullrolloutperformance. Notethatallofour
trainingdatacomesfromtherealworld(excepttheexperimentinSection6.3),andthesimulatoris
usedonlyformodelselection. Toaccomplishthis,weexpandthesimulationenvironmentproposed
byLeeetal.(2022b)tosupport551ofthetasksdescribedinSection5.2. Foreachofthesetasks,
we define a set of scene setup randomizations, robot pose randomizations, and success detection
criteria. Tobridgethevisualdistributionshiftbetweentherealworldandthesimulation, wetrain
a RetinaGAN (Ho et al., 2020) model that transforms simulated images into realistic looking im-
ages. Then,wedeploypoliciestrainedonrealdatadirectlyintothesesimulationenvironmentsby
applyingRetinaGANvisualtransformationsateachtimestepandmeasuringrolloutsimulatedtask
successrates.
Whilemodelstrainedonlyonrealworlddataperformbetterintherealworldthantheydoinsim-
ulation,wefindthatthesimulationsuccessratesofhigh-performingrealworldpoliciesarehigher
thanthesimulationsuccessratesoflow-performingrealworldpolicies.Inotherwords,theordering
of simulation policy success rates are informative for predicting the ordering of real world policy
successrates. Wenotethatinthisreal-to-simevaluationsetting, wehavealessstrictrequirement
for simulation accuracy compared to sim-to-real settings; as long as simulation success rates are
directionallycorrelatedwithrealsuccessrates,wecanacceptamoderateorevenhighgapbetween
realandsimulationsuccessrates.
WepresentexamplecameraimagesfromsimulationaswellastheirRetinaGAN-basedtransforma-
tionsinFig.8.
Figure8:Examplecameraimagesshowcasingrawsimulation,simulationwithRetinaGANapplied,
andtherealworld.
22

--- Page 23 ---
Preprint
C.4 DATACOLLECTIONPROCESS
Figure9showsthegrowthofdata,numberoftasks,andthesuccessrateofthepolicyovertime.The
numberoftasks/instructionsthatoursystemiscapableofgrowsovertimeasmoredataiscollected.
Thesameistruewiththeperformanceofseentasks.Oneoftheimportantaspectsofthefuturework
isdeveloptechniquesthatallowustogrowthedataaswellastherobotsperformanceandgeneral
capabilitiesatafasterrate.
Figure9: Thegrowthofdata,numberoftasks,andseeninstructionperformanceovertime.
D EXPERIMENTS
D.1 EVALUATIONDETAILS
InSection6.2, westudythezero-shotgeneralizationcapabilitiesofRT-1todifficultscenariosnot
present in the training dataset. To fairly evaluate different ablations of RT-1 as well as baseline
policies,wedesignstandardizedevaluationproceduresthatcoverarangeofincrementaldifficulty
levels.
Seen tasks. We evaluate on 744 tasks present in the training dataset. The breakdown between 12
skillsisshowninTable1. Forall“Seen”evaluations, weusethesameclassroomsettingusedfor
datacollectionasdescribedinSection5.2. Foreachpolicy,wereportasinglerepresentativemetric
thattakesaskill-weightedaverageacrossindividualskillevaluations.
Unseentasks. Weevaluatepolicyperformanceon53tasksthatareheldoutduringtraining. While
the unseen instructions’ specific combinations of skills and objects are not seen during training,
othercombinationsofthesameskillsandobjectsarepresentinthetrainingset. Weevaluatethese
unseentasksinthesameenvironmentandthesamerandomizationprocedureastheSeentasks. A
fulllistoftheseunseentasksisshowninTable8.
Distractorrobustness. Wetestthreetasks(“pickcokecan”,“placecokecanupright”,“movecoke
canneargreenricechipbag”)withincrementallymoredistractorobjectsaddedtothescene. The
easysettingincludes0,2,or5distractorobjects. Themediumsettingincludes9distractorobjects,
but the coke can is never obscured. The hard setting includes 9 distractor objects, but the scene
is more crowded and the coke can is partially occluded. Both the medium are hard setting are
more difficult than scenarios in the training dataset, which contained between 0 and 4 distractors.
ExamplesofthesedifficultysettingsandpolicyevaluationrolloutsareshowninFigure12.
Background robustness. We test six tasks (“pick coke can”, “move blue chip bag near or-
ange”, “knock redbull can over”, “pick green jalapeno chip bag”, “move sponge near brown chip
bag”,“place redbull can upright”) with incrementally more challenging backgrounds and counter
textures. Intheeasysetting,weutilizethesamebackgroundenvironmentsandcountertexturesas
thetrainingdataset. Inthemediumsetting,weutilizethesamebackgroundenvironmentbutadda
patternedtableclothtochangethecountertexture.Inthehardsetting,weutilizeabrandnewkitchen
environmentwithanewcountertop;thischangesthecountertexture,drawermaterialandcolor,and
23

--- Page 24 ---
Preprint
backgroundvisuals. Examplesofthesedifficultysettingsandpolicyevaluationrolloutsareshown
inFigure10.
Realistic instructions. To study how RT-1 performs in more realistic scenarios, we propose an
evaluation setting in a real office kitchen that is a dramatic shift from the original training class-
room environment. We propose a variety of skills that combine aspects of the previous zero-shot
evaluations, including adding new distractors, including new backgrounds, and new combinations
ofobjectswithskills. WerefertotheeasiestscenarioasL1generalization,whichintroducesanew
countertopandlightingconditionbutkeepstheskillsandobjectsthesame. Next,L2generalization
additionallyaddsnoveldistractorobjectssuchaskitchenjarcontainers. Finally,L3generalization
addsnewobjectsornewlocationssuchasnearasink. Whilesomeofthesedistributionshiftsare
tested in Section 6.2, these realistic instructions aim to test multiple dimensions simultaneously.
ExamplesoftheseinstructionsarepresentedinFig.11.
Easy
same background,
same texture
Medium
same background,
new texture
Hard
new background,
new texture
Figure 10: “Backgrounds” evaluations focus on testing the performance of RT-1 on settings with
differenttabletexturesanddifferentbackgrounds,suchasthosefoundinkitchensnevertrainedon.
These visual differences are quite pronounced, which in the most challenging case entails a new
kitchenwithdifferentcountertexture,differentlightingconditions,differentcountermaterial,anda
differentbackground.
Figure11:“Realisticinstructions”evaluationsproposerealisticscenariosmultipledistributionshifts
thatincrementallyincreaseindifficulty. L1generalizationintroducesanewrealofficekitchenwith
newlightingconditions. L2generalizationadditionallyaddsunseendistractorobjects. Finally,L3
generalizationincludesnewobjectsorobjectsinnewlocations,suchasnexttoasink.
D.2 HETEROGENEOUSDATA
WealsoexplorethelimitsofRT-1forutilizinghighlyheterogeneousdata.WedemonstratehowRT-
1canincorporateandlearnfromvastlydifferentdatasourcesandimprovefromsuchdatawithout
24

--- Page 25 ---
Preprint
Instruction
pickcokecanfromtopdrawerandplaceoncounter
pickgreencanfromtopdrawerandplaceoncounter
pickgreenricechipbagfrommiddledrawerandplaceoncounter
pickredbullcanfromtopdrawerandplaceoncounter
place7upcanintobottomdrawer
placebrownchipbagintotopdrawer
placegreencanintomiddledrawer
move7upcannearredbullcan
moveappleneargreenricechipbag
moveapplenearpaperbowl
moveapplenearredbullcan
movebluechipbagnearblueplasticbottle
movebluechipbagnearpepsican
movebluechipbagnearsponge
movebrownchipbagnearapple
movebrownchipbagneargreenricechipbag
movebrownchipbagnearredbullcan
movecokecanneargreenjalapenochipbag
movecokecannearwaterbottle
movegreencannear7upcan
movegreencannearapple
movegreencannearcokecan
movegreenjalapenochipbagnearbluechipbag
movegreenricechipbagnearorange
movegreenricechipbagnearorangecan
movegreenricechipbagnearpaperbowl
moveorangecannearbrownchipbag
movepepsicannearorangecan
moveredbullcannearcokecan
moverxbarblueberrynearblueplasticbottle
moverxbarblueberrynearorangecan
moverxbarchocolatenearpaperbowl
moverxbarchocolatenearrxbarblueberry
movespongenearapple
movewaterbottlenear7upcan
movewaterbottlenearsponge
movewhitebowlnearorangecan
pickblueplasticbottle
pickgreenricechipbag
pickorange
pickrxbarchocolate
picksponge
placepepsicanupright
knockorangecanover
pickblueplasticbottlefrompaperbowlandplaceoncounter
pickbrownchipbagfromwhitebowlandplaceoncounter
pickgreencanfrompaperbowlandplaceoncounter
pickgreenjalapenochipbagfromwhitebowlandplaceoncounter
pickorangecanfromwhitebowlandplaceoncounter
pickredbullcanfromwhitebowlandplaceoncounter
placeblueplasticbottleintopaperbowl
placecokecanintopaperbowl
placeorangecanintopaperbowl
Table8: ListofUnseenInstructionsinSec.6.2. Forthe“UnseenTasks”evaluation,weexcludea
totalof53tasksduringtraining. Whiletheseexactinstructionswerenotpresentinthetrainingset,
theobjectsandskillscontainedintheseinstructionswerestillpresentinthetrainingset.
25

--- Page 26 ---
Preprint
Easy
2 - 5 distractors,
no occlusion
Medium
9 distractors,
no occlusion
Hard
9 distractors,
occlusion
Figure12: “Distractors”evaluationsfocusondiversifyinginitialsceneconfigurationswellbeyond
thedistributionscontainedinthetrainingdataset,whichcontainbetween2and4distractorobjects.
Inthemostchallengingscenarios, thesceneisextremelyclutteredandcontainsocclusionsforthe
objectsofinterest.
sacrificingitsoriginal-tasksperformanceacrossthevariedtasksinherentinthisdata. Tothisend,
weconducttwoexperiments: (1)RT-1trainedandtestedonbothrealdataandsimulationdataand
(2)RT-1trainedacrosslargedatasetsofdifferenttasks,originallycollectedbydifferentrobots.
Absorbingsimulationdata. Table9showstheabilityofRT-1, andbaselines,toabsorbbothreal
and simulation data. To test this, we take all of the real demonstration data but we also provide
additionalsimulationdatathatincludesobjectsthattherobothasneverseenintherealworld. We
addasetofsimobjectsandonlyshowthemonasubsetoftasks,specificallythepickingtasks,in
simulation. To accomplish this, we run our real2sim method described in Sec. C.3 to bootstrap a
simulation policy from the real world policy that is then trained with multi-task RL (Kalashnikov
etal.,2021a)withadditionalobjectsinsimulation. Fromthisprocess, weextract518ksuccessful
trajectories of picking new objects and mix them with the real data that was used in the previous
experiments. Thegoalofthisexperimentistodemonstratethatbyexpandingthedatasetofsimu-
lationtrajectories,wecanbenefitRT-1’sgeneralizationcapabilitieswithoutsacrificingtheoriginal
trainingperformance–adesiredpropertyofanabsorbentmodel.
Toevaluatethepropertiesofthismodel,wespecifydifferentgeneralizationscenarios:forseenskills
withrealobjectsthetrainingdatahasrealdataofthatinstruction(i.e.,performanceonseentasks),
forseenskillswithsimobjectsthetrainingdatahassimdataofthatinstruction(e.g. “pickupasim
object”,whichwaspresentinsim),andforunseenskillswithsimobjectsthetrainingdatahassim
dataofthatobjectbuttherearenoexamplesoftheinstructiondescribingtheskillwiththatobject
eitherinsimorinreal(e.g.,“moveasimobjecttoapple”,eventhoughtherobothasonlypracticed
inpickingthatsimobjectandnotmovingitnearotherobjects). Allevaluationsaredoneinthereal
worldbuttolimitthenumberofinstructionsevaluated,wefocusonpickandmove-toskills.
We find in Table 9 that for RT-1, we do not lose performance adding simulation data compared
to the Real Only dataset. We do however, see a significant increase in performance (from 23% to
87%)onobjectsandtasksseenonlyinsimulation, toapproximatelytheperformanceofthethose
in real, demonstrating an impressive degree of domain transfer. We also see a significant increase
inperformanceonunseeninstructionsfrom7%to33%;impressivegiventheobjectinquestionhas
never been seen in real and the instruction never seen at all. Overall, we find that RT-1 is able to
efficiently“spongeup”newdata,evenfromaverydifferentdomain.
26

--- Page 27 ---
Preprint
60%
50%
RealObjects SimObjects(notseeninreal)
40%
SeenSkill SeenSkill UnseenSkill
Models TrainingData w/Objects w/Objects w/Objects 30%
RT-1 RealOnly 92 23 7 20%
RT-1 Real+Sim 90 87 33
10%
0%
Sim-seen Objects Sim-seen Objects Real Tasks
w/ Skills w/o Skills
ot
derapmoC
etaR
sseccuS
ylno
laeR
Real +Sim Data
+64%
+26%
-2%
Table 9: Experimental results for incorporating simulation data in RT-1. Adding simulation data
doesnotimpacttheperformanceonrealobjects,whilesignificantlyimprovingrealperformanceon
objectsthatwereonlyintroducedinsimulation.
Absorbing data from different robots. To push the data absorption limits of RT-1, we conduct
an additional set of experiments where we combine two data sources that originate from different
robots: Kuka IIWA as well as the Everyday Robots mobile manipulators used in the experiments
sofar. TheKukadatacontainsallthesuccessfulexamplescollectedinQT-Opt(Kalashnikovetal.,
2018),whichcorrespondsto209kepisodes,wheretherobotwasindiscriminatelygraspingobjects
inabin(seeanexampleofaKukaepisodeinTable.10). Ourgoalinthisexperimentistoanalyze
whethertheperformanceontheRT-1tasksdropswhenaddingtheadditionaldataand,moreimpor-
tantly,whetherwecanobserveanytransferfromdatacollectedbyadifferentrobotmorphology.
Wewouldliketoemphasizethedifficultyofthissettingbynotingthemajordifferencesbetweenthe
datasets. Notonlyaretherobotsthatcollectedthedatadifferentinappearanceandactionspace,but
alsotheenvironmenttheyweredeployedinhasdifferentappearanceanddynamics. Inadditionthe
QT-Optdatapresentsacompletelydifferentactiondistribution–itwascollectedbyanRLagentas
opposedtohumandemonstrationspresentinourdataset.
TomixtheKukadatatogetherwiththeRT-1data,wefirsttransformtheoriginalKuka4-DOFaction
spaceintothesameactionspaceasRT-1,namelywesettherollandpitchto0,whilekeepingtheyaw
valuesthatwerepresentintheoriginalKukadata.Inaddition,wetransformthebinarygripper-close
commandintoacontinuousgripper-closednesscommandthatispresentintheRT-1data. Wealso
needtextinstructionscorrespondingtothetaskperformedandsincetheKukadatadoesnotcontain
thenameoftheobjectthatwasgrasped, werelabelallthedatatothe“pickanything”instruction.
Withthesemodifications,wemixbothdatasetswiththe2:1(RT-1data: Kukadata)ratioandtrain
RT-1toobtainthefinalmodel.
TotestwhetherRT-1caneffectivelyabsorbthesetwoverydifferentdatasets, weevaluatetheper-
formance on the original RT-1 tasks (in this case, we also focus on “pick” and “move to” skills),
whichwerefertoasthestandard“Classroomeval”,aswellastheperformanceonthenewlycon-
structed tasks that reflect the bin-picking setup present in the Kuka data, which we refer to as the
“Bin-pickingeval”. FortheBin-pickingevaltobeclosetotheoriginaldataset,weputinthesame
looking bin for the objects as well as modify the robot to be similar to the Kuka manipulators by
adding extra wires and coloring the gripper gray. For all of the evaluations we use the Everyday
Robotsrobotwiththepickingcommandsandevaluateitbasedon72graspingtrials.
TheresultsarepresentedinTable10. WeobservethatthemodelthatmixestheRT-1dataandthe
Kukadatahasonlyaminimaldecreaseintheoriginaltasks’performance(i.e. Classroomeval),i.e.
2%. Even more importantly, in the Bin-picking eval, we observe that the model trained on multi-
robotdataperformsat39%comparedtothe22%ofthemodelthatwastrainedonlyontheRT-1data.
Thisisa17%performancedifference(almost2x). Additionally,RT-1trainedonKukabin-picking
data and evaluated on the bin-picking tasks with the Everyday Robots (EDR) robot achieves 0%
performance, confirming that it is difficult to transfer a behavior from another robot morphology.
However, mixing the data from both robots allows RT-1 to infer the correct actions of the EDR
robot even when faced with the states observed by Kuka robots. This is achieved without explicit
demonstrationsofbin-pickingonEDRrobotandbytakingadvantageofpastexperiencescollected
byKukarobots. TheseresultsindicatethatRT-1’sabsorptionpropertiesalsoincludetheabilityto
27

--- Page 28 ---
Preprint
17.5%
15.0%
12.5% Models TrainingData Classroomeval Bin-pickingeval
10.0%
RT-1 Kukabin-pickingdata+EDRdata 90 39
7.5%
RT-1 EDRonlydata 92 22
5.0% RT-1 Kukabin-pickingonlydata 0 0
2.5%
0.0%
2.5%
Bin-picking Eval Classroom Eval
ylnO
RDE
ot
derapmoC
etaR
sseccuS
EDR +Kuka Data
+17%
-2%
Table 10: Experimental results for mixing data from two different robots. Incorporating Kuka
bin-picking data from QT-Opt (Kalashnikov et al., 2018) in RT-1 minimally impacts the standard
classroomevaluationperformanceandresultsinalmosta2ximprovementingeneralizationtothe
Bin-picking evaluation (that is similar to the setup in the Kuka data) on the Everyday Robots ma-
nipulator. Thisdemonstratesaneffectivetransferacrosstwodifferentrobotmorphologies.
acquire new skills through observing other robots’ experiences and present an exciting avenue of
futureworkwherewecombinemanymoremulti-robotdatasetstoenhancetherobotcapabilities.
D.3 LONG-HORIZONEVALUATIONDETAILS
Inadditiontoshort-horizonindividualskillevaluationsshowninprevioussections,wealsoevaluate
howRT-1performsinalong-horizonrealistickitchensettingthatchainsmultiplemanipulationand
navigation skills to accomplish natural language instructions within the SayCan framework (Ahn
etal.,2022). Alistoflong-horizoninstructionsusedfortheseevaluationsislistedinTable12.
Thesuccessrateoflong-horizontasksdecreasesexponentiallywiththelengthofthetask,sohigh
successratesinmanipulationskillsareparticularlyimportant. Furthermore,asmobilemanipulation
tasks require both navigation and manipulation, the policies ability to be robust to base position
iscrucial. SinceSayCancombinesmanylow-levelinstructionstoperformhigh-levelinstructions,
the number of possible high-level instructions increases combinatorially with instructions, so the
skill-breadthofRT-1canbefullyseen.
SayCan works by grounding language models in robotic affordances and it leverages few-shot
prompting to break down a long horizon task expressed in natural language to a sequence of low
level skills. An example of long horizon task would be “Bring me two different sodas”, and one
feasibleplanwouldbe“1. findacoke,2. pickupthecoke,3. bringittoyou,4. putdownthecoke,
5. findapepsi,6. pickupthepepsi,7. bringittoyou,8. putdownthepepsi,9. done.” Toobtainthe
affordancefunctionweusevaluefunctionstrainedwithMT-OPT(Kalashnikovetal.,2021a). Fora
detaileddescriptionofSayCanalgorithmpleasereferto (Ahnetal.,2022).
Sincethefocusofthispaperisacquisitionofmanygeneralizableskills,wefocusourevaluationon
onesubsetoftaskspresentedin Ahnetal.(2022).Itisthelong-horizonfamilyoftasks,involving15
instructions,eachinstructionrequiresanaverageof9.6stepstocomplete,andinvolvesanaverage
of2.4manipulationskillsperinstruction. AfulllistoftheinstructionscanbefoundinTable12.
Wecompareagainst3baselines.1)SayCanwithBC-Z,whichusesSayCanplanningalgorithmwith
BC-Z as manipulation policy, 2) SayCan with Gato, which uses SayCan planning algorithm with
Gato as manipulation policy, 3) Originally reported SayCan results, which use SayCan planning
algorithmwithBC-Z,butsinceitusesaslightlydifferentprompt,theplanningsuccessrateislower.
Wereimplemented3)in1)forafaircomparison.
AsshowninTable11,exceptfororiginalSayCan,allmethodsget87%asplanningsuccessrate,and
RT-1performsthebest,with67%executionsuccessrateinKitchen1. Kitchen2constitutesamuch
morechallenginggeneralizationscene,sincetheRobotClassroomtrainingscenesaremodeledafter
Kitchen1 (see the pictures of the kitchens in Fig. 2). Due to this generalization difficulty, SayCan
with Gato is not able to finish any long horizon task, and SayCan with BC-Z is able to achieve a
success rate of 13%. The original SayCan paper did not evaluate performance in a new kitchen.
Surprisingly,themanipulationperformancedoesnotseeavisibledropfromKitchen1toKitchen2
28

--- Page 29 ---
Preprint
forourmethod. Inthesupplementaryvideo,weshowthatthisenablesustooperateunseendrawers
inKitchen2,andthatwecanuseSayCan-RT1toplanandexecuteultra-longhorizontasks,withas
manyas50steps.
SayCantasksinKitchen1 SayCantasksinKitchen2
Planning Execution Planning Execution
OriginalSayCan(Ahnetal.,2022)∗ 73 47 - -
SayCanw/Gato(Reedetal.,2022) 87 33 87 0
SayCanw/BC-Z(Jangetal.,2021) 87 53 87 13
SayCanw/RT-1(ours) 87 67 87 67
Table11: SayCanstylelonghorizontasksinKitchen1andKitchen2. (*OriginalSayCanevaluses
aslightlydifferentpromptsotheplanningsuccessrateislower.)
D.4 MODELABLATIONS
What are the important and practical decisions in the design of the model and how do they
affectperformanceandgeneralization?
To answer this question, we perform a set of ablations over different design decisions in RT-1.
We aim to test a number of hypotheses that will help us disambiguate where the benefits of our
methodcomefrom. Possiblehypothesesaboutthesourceofimprovementinclude: (i)thecapacity
andexpressivenessofourmodel,whichweverifybyablatingthemodelsize,tryingotherarchitec-
tures(e.g.,byremovingtheTransformercomponent);(ii)theparticularactionrepresentation,which
makesiteasytorepresentcomplexmulti-modalactiondistributions,whichwetestbyswitchingto
continuous(normallydistributed)actions,aswellasbyablatingtheauto-regressiveactionrepresen-
tation;(iii)theImageNetpre-trainedinitializationofthecomponents,whichwetestbyinitializing
themodel’sweightsrandomly;and(iv)accesstotheshorthistory,whichwetestbyexcludingob-
servationhistory.Moreconcretely,weablateourmodelby(1)decreasingthemodelsize(from35M
to21Mparameters),(2)removingtheTransformerarchitecture(usingapre-trainedEfficientNetin-
stead),(3)usingacontinuousinsteadofdiscreteactionspace(usinganMSElossandmultivariate
normaloutput), (4)auto-regressivelyconditioningonactions, (5)removingImageNetpre-training
of the FiLM EfficientNet, and (6) removing history (reducing the sequence of six images as input
to a single image). For each ablation we compare on the axes of performance on seen tasks, per-
formanceonunseentasks,aswellasinferencespeedandrobustnesstodistractorsandbackgrounds
(withamoredetaileddescriptionofeachcategoryinSection6.1andAppendixD.1).
Table 13 shows the results of each ablation and the delta performance compared to the full RT-1.
RT-1achievesimpressiveperformanceontasksandnewenvironments,andparticularlyoutperforms
baselines on the most challenging robustness problems. We also find that each design decision is
important,thoughatvaryinglevels. Wefirstevaluateamodelthatreplacestheper-dimensiondis-
cretizedactionrepresentationinourmodelwithamorestandardcontinuousGaussiandistribution.
We observe a significant decline in performance from this modification. The per-dimension dis-
cretization allows our model to represent complex multi-modal distributions, while the Gaussian
distributioncapturesonlyasinglemode. Theseresultssuggestthatthisstandardandpopularchoice
ishighlysuboptimalwiththemorecomplexanddiversedemonstrationdatausedbyoursystem.Im-
ageNetpre-trainingisparticularlyimportantformodelgeneralizationandrobustness,decreasingthe
unseentaskperformancerateby33%, asaresultofthelargeanddiversevisualsoftheImageNet
dataset. Adding history has an impact primarily on generalization to distractors, while removing
theTransformercomponenthasauniformbutsmallnegativeimpactacrosstheseentasks, unseen
tasksanddistractors. InordertokeeptheImageNetpre-trainingwhilereducingthemodelsize,we
reduce the number of parameters only by 40% (from 31M to 25M). Resulting performance drops
across training and generalization tasks but not as much as in other ablations. Finally, autoregres-
sivelyconditioningonactions, asusedin(Reedetal.,2022;Chenetal.,2021;Leeetal.,2022a),
didnotbenefitperformanceandslowedinferencebymorethan2x.
AsdescribedinSec.5.1,inordertorunlargeTransformermodelsonrealrobots,werequireamodel
thatsupportsfastinferenceforreal-timeoperation. Notethatinordertoachieveourtargetcontrol
rateof3Hz(describedinSec.5.1),wealsoneedtoconsiderothersourcesoflatencyinthepipeline,
such as the camera latency and communication overhead. However, these factors will be constant
29

--- Page 30 ---
Preprint
Instruction
Howwouldyouputanenergybarandwaterbottleonthetable
Howwouldyoubringmealimesodaandabagofchips
Canyouthrowawaytheappleandbringmeacoke
Howwouldyoubringmea7upcanandatea?
Howwouldthrowawayalltheitemsonthetable?
Howwouldyoumoveanmultigrainchipstothetableandanappletothefarcounter?
Howwouldyoumovethelimesoda,thesponge,andthewaterbottletothetable?
Howwouldyoubringmetwosodas?
Howwouldyoumovethreecokestothetrashcan?
Howwouldyouthrowawaytwocokes?
Howwouldyoubringmetwodifferentsodas?
Howwouldyoubringmeanapple,acoke,andwaterbottle?
Ispilledmycokeonthetable,howwouldyouthrowitawayandthenbringmesomething
tohelpclean?
Ijustworkedout,canyoubringmeadrinkandasnacktorecover?
Howwouldyoubringmeafruit,asoda,andabagofchipsforlunch
Table12: ListofSayCaninstructionsevaluatedinSec.6.4
Distractors Backgrounds
Model SeenTasks UnseenTasks All Easy Medium Hard All InferenceTime(ms)
Gato(Reedetal.,2022) 65(-32) 52(-24) 43(-40) 71 44 29 35(-24) 129
BC-Z(Jangetal.,2021) 72(-25) 19(-57) 47(-36) 100 67 7 41(-18) 5.3
BC-ZXL 56(-41) 43(-33) 23(-60) 57 33 0 35(-24) 5.9
RT-1(ours) 97 76 83 100 100 64 59 15
RT-1w/obigmodel 89(-8) 62(-14) 77(-6) 100 100 50 53(-6) 13.5
RT-1w/opre-training 84(-13) 43(-33) 60(-23) 100 67 36 41(-18) 15
RT-1w/continuousactions 68(-29) 43(-33) 37(-46) 71 67 0 35(-24) 16
RT-1w/auto-regressiveactions 85(-12) 71(-5) 67(-16) 100 78 43 65(+6) 36
RT-1w/ohistory 82(-15) 62(-14) 50(-33) 71 89 14 59(+0) 15
RT-1w/oTransformer 86(-13) 62(-14) 67(-16) 100 100 29 59(+0) 26
Table 13: Various model ablations of RT-1 across seen tasks, generalization to unseen tasks, and
robustnesstodistractorsandbackgrounds.
for all the models, and therefore we focus our evaluation on just the network inference time. The
last column of Table 13 shows the inference speed of all the models. RT-1 is almost an order of
magnitudefasterthanGatowithasimilarnumberofparameters,butitisalsoconsiderablyslower
than a ResNet-based BC-Z. In terms of the different ablations of our model, we observe that the
biggestslow-downiscausedbyincludingauto-regressiveactions(∼2xslow-down),andsincethis
doesnotsignificantlyinfluencetheperformance,thefinalversionofRT-1doesnotgenerateactions
auto-regressively.
30

--- Page 31 ---
Preprint
D.5 SUMMARYANDANALYSIS
In this section, we summarize some of our findings and propose intuition for RT-1’s high perfor-
mance,generalization,androbustness. First,ImageNetpretraining(alongwithUniversalSentence
Encoder language embedding) has a large impact particularly on unseen tasks. We observe that
RT-1 inherits some of the knowledge that results from the generality and diversity of the datasets
thesemodelsweretrainedon. Second,continuousactionshavealargeimpactacrossallaspectsof
performance. This has been previously observed and may be due to the ability to represent more
complexactiondistributions–theper-dimensiondiscretizationallowsourmodeltorepresentcom-
plexmulti-modaldistributions,whiletheGaussiandistributioncapturesonlyasinglemode. Third,
given such expressive multitask models, data diversity has a larger impact than data size. Indeed,
even datasets collected in simulated environments or from different robotic embodiments can be
leveragedbyRT-1,openingavenuesfornewregimesofdatacollection.
Finally,RT-1fuseslanguageintotheimagepipelineearlyviaFiLMconditioning,comparedtoe.g.,
Gato’slatefusion. Thisenablesimagetokensthatfocusonlyonrelevantfeaturesfortheinstruction
at hand, which may be the cause of poor distractor performance for Gato. Figure 13 visualizes
theattentionduringrolloutsofRT-1. Weseethattheattentionisfocusedonrelevantfeaturesand
particularlyoninteractionbetweenthegripperandtheobjectofinterest.Thebottleneckofattention
layers such as these results in a compact representation which effectively ignores distractors and
varyingbackgrounds.
“pick green
jalapeno chip
Layer 2, bag from middle
Head 6 drawer and
place on
counter”
“place rxbar
Layer 2,
blueberry in
Head 6
bottom drawer”
Layer 4,
“open middle
Head 2
drawer”
Figure13: InthisfigureweshowtheattentionmapoftheRT-1policy. Differentlayersandheads
generallyfocusondifferentpartoftheimage. Mostcommonly,theyfocusonthepartsofthescene
with the richest interaction affordances, such as graspable objets. For example, Layer 2 Head 6
focuses on the jalapeno chips and pepsi can in grasping tasks; and Layer 4 Head 2 focuses on the
drawerindraweropeningtasks.
31