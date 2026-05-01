--- Page 1 ---
R3M: A Universal Visual Representation
for Robot Manipulation
SurajNair1,∗,AravindRajeswaran2,VikashKumar2,ChelseaFinn1,AbhinavGupta2
1StanfordUniversity,2MetaAI
Abstract:Westudyhowvisualrepresentationspre-trainedondiversehumanvideo
datacanenabledata-efficientlearningofdownstreamroboticmanipulationtasks.
Concretely, we pre-train a visual representation using the Ego4D human video
datasetusingacombinationoftime-contrastivelearning,video-languagealignment,
andanL1penaltytoencouragesparseandcompactrepresentations. Theresulting
representation,R3M,canbeusedasafrozenperceptionmodulefordownstream
policylearning. Acrossasuiteof12simulatedrobotmanipulationtasks,wefind
thatR3Mimprovestasksuccessbyover20%comparedtotrainingfromscratch
andbyover10%comparedtostate-of-the-artvisualrepresentationslikeCLIPand
MoCo. Furthermore,R3MenablesaFrankaEmikaPandaarmtolearnarange
ofmanipulationtasksinareal,clutteredapartmentgivenjust20demonstrations.
Codeandpre-trainedmodelsareavailableathttps://tinyurl.com/robotr3m.
Keywords: VisualRepresentationLearning,RoboticManipulation
1 Introduction
How do we train a robot to complete a manipulation task from images? A standard and widely
usedapproachistotrainanend-to-endmodelfromscratchusingdatafromthesamedomain[1].
However, this can be prohibitively data intensive and severely limits generalization. In contrast,
computervisionandnaturallanguageprocessing(NLP)haverecentlytakenamajordeparturefrom
this“tabularasa”paradigm. Thesefieldshavefocusedonusingdiverse,large-scaledatasetstobuild
reusable,pre-trainedrepresentations. Suchmodelshavebecomeubiquitous;forexample,visual
representationsfromImageNet[2]canbereusedfortaskslikecancerdetection[3],andpre-trained
languageembeddingslikeBERT[4]havebeenusedforeverythingfrommedicalcoding[5]tovisual
questionanswering[6]. SuchanequivalentofanImageNet[2]orBERT[4]modelforrobotics,that
canbereadilydownloadedandusedforanydownstreamsimulationorreal-worldmanipulationtask,
hasremainedelusive.
Whyhavewestruggledinbuildingthisuniversalrepresentationforrobotics? Ourconjectureisthat
wehaven’tconvergedonusingtheappropriatedatasetsforrobotics. Collectinglargeanddiverse
datasetsofrobotsinteractingwiththephysicalworldcanbecostly,evenwithouthumanannotation.
Recent attempts at creating such datasets [7, 8, 9, 10], consist of a limited number of tasks in at
mostahandfulofdifferentenvironments. Thislackofdiversityandscalemakesitdifficulttolearn
representationsthatarebroadlyapplicable. Atthesametime,therecenthistoryofcomputervision
andNLPsuggestsanalternaterouteforrobotics. Thebestrepresentationsinthesefieldsdidnot
ariseoutoftask-specificandcarefullycurateddatasets,butrathertheuseofabundantin-the-wild
data[4,11,12,13]. Analogously,forroboticsandmotorcontrol,wehaveaccesstovideosofhumans
interactinginsemanticallyinterestingwayswiththeirenvironments[14,15,16]. Thisdataislarge
anddiverse,spanningscenesacrosstheglobe,andtasksrangingfromfoldingclothestocookinga
meal. Whiletheembodimentpresentinthisdatadiffersfrommostrobots,priorwork[17,18]has
foundthatsuchhumanvideodatacanstillbeusefulforlearningrewardfunctions. Furthermore,
domaingaphasnotbeenamajorbarrierforusingpre-trainedrepresentationsintraditionalvisionand
6thConferenceonRobotLearning(CoRL2022),Auckland,NewZealand.
∗WorkcompletedduringinternshipatMetaAI
2202
voN
81
]OR.sc[
3v10621.3022:viXra

--- Page 2 ---
Time Contrastive Learning
Ego4D Video +
Language
Video-Language Alignment
“stirs the “removes the
snacks…” battery…”
M3R
deniarT-erP
noitatneserpeR
Efficient Robot Learning
New Environment, New Tasks
time L1 Sparsity Penalty
Figure1: Pre-TrainingReusableRepresentationsforRobotManipulation(R3M):Wepre-trainavisual
representationusingdiversehumanvideodatasetslikeEgo4D[16],andstudyitseffectivenessfordownstream
robotmanipulationtasks.Ourrepresentationmodel,R3M,istrainedusingacombinationoftime-contrastive
learning,video-languagealignment,andanL1sparsitypenalty.WefindthatR3Menablesdataefficientimitation
learningacrossseveralsimulatedandreal-worldrobotmanipulationtasks.
NLPtasks. Inthisbackdrop,weaskthepertinentquestion: canvisualrepresentationspre-trainedon
diversehumanvideosenableefficientdownstreamlearningofroboticmanipulationskills?
Wehypothesizethatagoodrepresentationforvision-basedroboticmanipulationconsistsofthree
components. First,itshouldcontaininformationnecessaryforphysicalinteraction,andthusshould
capturethetemporaldynamicsofthescene(i.e. howstatesmighttransitiontootherstates). Second,
itshouldhaveaprioroversemanticrelevance,andshouldfocusontaskrelevantfeatureslikeobjects
andtheirrelationships. Finally,itshouldbecompact,andnotincludefeaturesirrelevanttotheabove
criteria(e.g. backgrounds). Towardssatisfyingthesethreecriteria,westudyarepresentationlearning
approach that combines (1) time contrastive learning [19] to learn a representation that captures
temporaldynamics,(2)video-languagealignmenttocapturesemanticallyrelevantfeaturesofthe
scene,and(3)L1andL2penaltiestoencouragesparsity. OurexperimentalevaluationinSection4.4
findsthatallthreecomponentsareimportantfortraininghighlyperformantrepresentations.
Inthisworkweempiricallydemonstratethatrepresentationspre-trainedondiversehumanvideo
datasetslikeEgo4D[16]canenableefficientdownstreampolicylearningforroboticmanipulation.
Our core contribution is an artifact – the pre-trained vision model – that can be used readily in
other work. Concretely, we pre-train a reusable representation for robotic manipulation (R3M),
whichcanbeusedasafrozenperceptionmodulefordownstreampolicylearninginsimulatedand
realrobotmanipulationtasks. Wedemonstratethisviaextensiveexperimentalresultsacrossthree
existing benchmark simulation environments (Adroit [20], Franka-Kitchen [21], and MetaWorld
[22])aswellasrealrobotexperimentsinaclutteredapartmentsetting. R3Mfeaturesoutperform
awiderangeofvisualrepresentationslikeCLIP[12],(supervised)ImageNet[2],MoCo[23,24],
andlearningfromscratchbyover10%whenevaluatedacross12tasks,9viewpoints,and3different
simulation environments. On a Franka Emika Panda robot, R3M enables learning challenging
tasks like putting lettuce in a pan and folding a towel with a 50+% average success rate, given
lessthan10minutesofhumandemonstrations(seeFigure1),whichisnearlydoublethesuccess
rate compared to CLIP features. Overall, on the basis of these results, we believe that R3M has
the potential to become a standard vision model for robot manipulation, which can be simply
downloaded and used off-the-shelf for any robot manipulation task or environment. See https:
//sites.google.com/view/.robot-r3mforpre-trainedmodelsandcode.
2 RelatedWork
RepresentationLearningforRobotics. Ourworkiscertainlynotthefirsttostudytheproblemof
learninggeneralrepresentationsforrobotics. Onelineofworkfocusesonlearningrepresentations
from in-domain data, that is, using data from the target environment and task for training the
representation. Suchmethodsincludecontrastivelearningwithdataaugmentation[25,26,27,28],
dynamics prediction [29, 30], bi-simulation [31], temporal or goal distance [32, 33], or domain
specific information [34]. However, because they are trained on data exclusively from the target
domainandtask,thelearnedrepresentationsfailtogeneralizeandcannotbere-usedtoenablefaster
learninginunseentasksandenvironments.
2

--- Page 3 ---
Recently,therehasbeengrowinginterestinlearningmoregeneralrepresentationsformotorcontrol
from large-scale out-of-domain data like images from the web. This includes the use of CLIP,
supervised MS-COCO, supervised ImageNet, MoCo ImageNet features, or data from different
robots [35, 36, 37, 38, 23, 39]. In contrast to prior work, we pre-train the representation using
diversehumanvideoandlanguagedata,asopposedtostaticframesand/orclasslabels. Further,in
ourexperimentalevaluation,weobservethatourpre-trainedrepresentationoutperformspriorwork
significantlyonacomprehensiveevaluationsuite. Concurrently,Xiaoetal.[40]alsoexploretheuse
ofhumaninteractiondatatopre-trainvisualrepresentationsformotorcontrol. Howevertheirlearned
representationonlyusesstaticframesfromthesevideosanddoesnotutilizetemporalorsemantic
informationlikeR3M.Furthermore,ourevaluationfocusesondataefficientimitationlearning,and
enablesreal-worldlearninginclutteredenvironmentswithjust∼10minutesofdemonstrationdata.
LeveragingHumanVideosforRobotLearning. Severalpriorworkshaveexploredusinghuman
video data in robot learning, for example to acquire goals [41, 42, 43], to learn visual dynamics
models[44,45,46,47],ortolearnrepresentationsandrewards[19,48,49,50,51,52]. However,
thesepriorworkstypicallyfocusonasmalldatasetofhumanvideoscloselyresemblingtherobot
environment. Incontrast,ourworkleveragesdiversehumanvideodatalikeEgo4D[16]tolearn
visualreusablevisualrepresentationsthatgeneralizebroadly.
Natural Language and Robotic Manipulation. Prior works have explored the use of natural
languageinrobotmanipulation,primarilyasameansoftaskspecification[53,54,36,55]orreward
learning[56].Incontrast,weusediversehumanvideodataandlanguageannotationstolearnreusable
visual representations for control. Prior work has also found visual representations informed by
language,likeCLIP[12],tobeeffectiveforcontrol[36,37]. Throughempiricalevaluations,wefind
thatourR3MrepresentationsubstantiallyoutperformsCLIPforrobotmanipulation.
Learning from Diverse Robot Data. Towards robots that generalize more broadly, there are a
numberofworksthatstudyhowtoscaleupthesizeanddiversityofdatarobotslearnfrom. Manyof
theseworksfocusoncollectingandlearningfromrobotdataitself[57,58,7,8,9,10,59]. However,
theseworksoftencontainatmostahandfulofdifferentenvironments,makinggeneralizationacrossa
rangeofunseenscenesdifficult. Whilewealsoaimtoenablegeneralizationbylearningfromdiverse
data,ourfocusisinsteadon(1)learningfromhumanvideodataandhencealargerdistributionof
environmentsandtasks,and(2)pre-trainingavisualrepresentation,asopposedtopoliciesormodels.
Representation Learning from Videos. Finally, there is a rich literature of works that study
learningimagerepresentationsfromvideos[60,61,19,62,63,64]outsideofthecontextofrobotics.
Additionally,thereareanumberofworksthatuselanguagetolearnrepresentationsfromvideos
[65,66]. Critically,unlikealloftheseworks,themaincontributionofthisworkisnottoproposea
novelrepresentationlearningapproach,butratherinstudyingifrepresentationstrainedondiverse
videoandlanguageofhumaninteractioncanenablemoreefficientlearningofroboticmanipulation.
3 R3M:ReusableRepresentationsforRoboticManipulation
Ourgoalistousediversehumanvideodatatopre-trainasinglereusablevisualrepresentationfor
motorcontrol,particularlyroboticmanipulation,thatcanenableefficientdownstreamlearningin
previouslyunseenenvironmentsandtasks. Inthissection,wecoverthedifferentcomponentsofour
approach,beginningbydescribingourproblemformulationinSection3.1,thedatasourcesweuse
inSection3.2,andourtrainingobjectiveinSection3.3.
3.1 Preliminaries
Formally, weassumethatwehaveaccesstoadatasetD ofN videos, whereeachvideoconsists
of a sequence of RGB frames [I ,I ,...,I ]. Additionally, we assume that each video is paired
0 1 T
with a natural language description l, that describes what task is being completed in the video.
Fromthisdata,ourgoalistolearnasingleimageencoderF ,thatmapsimagestoadeterministic,
φ
continuousembedding,thatisz =F (I). Oncetrained,wewanttobeabletorepeatedlyreuseF for
φ
downstreampolicylearning. Specifically,thedownstreamproblemwillinvolveanagentsequentially
choosingactionsgivenimageobservationsI,andinsteadofusingrawimagesasinput,theagentwill
usethepre-trainedF (I)asastaterepresentation.
φ
3

--- Page 4 ---
“stirs the snacks in a
pan with a strainer
within her left hand”
“wiping the window
with the rag”
“stirs the snacks in a
pan with a strainer
within her left hand”
“picks up a piece of
wood from the
workbench with his
right hand”
- +
time
Figure2: Ego4D[16]VideoandLanguage(left). SampleframesandassociatedlanguagefromGrauman
et al. [16] used for training R3M. R3M Training (right). We train R3M with time contrastive learning,
encouragingstatescloserintimetobecloserinembeddingspaceandvideo-languagealignmenttoencourage
theembeddingstocapturesemanticallyrelevantfeatures.
3.2 DataSources
ForourlearnedrepresentationF tobeusefulinawiderangeofdownstreamtasksandenvironments,
φ
itshould(1)betrainedondatathatisdiverseenoughtofacilitategeneralization,and(2)providea
usefulsignalforfeaturesrelevanttoroboticmanipulation. Oneapproachwouldbetobeusenatural
imagesofftheweb(e.g. ImageNet[2]). Whilediverse,theseimagestendtofocusononeparticular
object,anddonotcaptureanagentinteractingwithmultipleobjectsinascene. Alternatively,dataof
humansinteractingintheworld[14,65,16]isbothdiverseandcontainsusefulinteractioninscenes
similartothosewewouldlikerobotstointeractin. Ofthemanyhumanvideodatasets,weleverage
theEgo4Ddataset[16]duetoit’sdiversityandsize,althoughinprincipleourmethodcanbeused
onanysuitablevideodataset. Ego4Dcontainsvideosofpeopleengaginginawiderangeoftasks
fromcookingtosocializingtoassemblingobjectsfrommorethan70locationsacrosstheglobe,and
intotalcontainsmorethan3500hoursofdata. Eachvideoclipalsocontainsanaturallanguage
annotationdescribingthebehaviorofthepersoninthevideo(SeeFigure2(left)).
3.3 Training R3M
Whatshouldagoodrepresentationforroboticmanipulationfromhumanvideodatacapture? We
propose three key components: (1) it should capture temporal dynamics, as the agent will be
sequentiallyinteractingintheenvironmenttoaccomplishtasks,(2)itshouldcapturesemantically
relevantfeatures,and(3)itshouldbecompact.Wenextdescribehowweusetimecontrastivelearning
tocapture(1),video-languagealignmentfor(2),andtheuseofL1regularizationtoencourage(3).
SeeFigure2(right)foranoverviewofourtrainingobjective.
TimeContrastiveLearning. ToencourageF tocapturefeaturesrelevanttophysicalinteraction
φ
andsequentialdecisionmaking,thefirstpartofourobjectiveisatimecontrastiveloss[61]. Given
abatchofvideoswetraintheencodertoproducearepresentationsuchthatthedistancebetween
imagescloserintimeissmallerthanforimagesfartherintimeorfromdifferentvideos. Specifically,
wesampleabatchofsequencesofframes[I ,I ,I ]1:B,thenminimizetheInfoNCEloss[67]:
i j>i k>j
(cid:88) eS(z i b,z j b)
L =− log (1)
tcn
b∈B
eS(z
i
b,z
j
b)+eS(z
i
b,z
k
b)+eS(z
i
b,z
i
(cid:54)=b)
wherez = F (I), andz(cid:54)=b isanegativeexamplesampledfromadifferentvideointhebatch. S
φ i
denotesameasureofsimilarity,whichinourcaseisimplementedasthenegativeL2distance.
Video-LanguageAlignment. ToencourageF tocapturesemanticallyrelevantfeatures,wetraina
φ
languagepredictionmodulefromtheembeddingoutputtedbyF . Essentially,bycapturingfeatures
φ
predictiveoflanguage,like“puttingtheappleontheplate”,thelearnedrepresentationshouldcapture
4

--- Page 5 ---
semantically relevant parts of the scene like the plate and apple state, that are likely relevant to
downstreammanipulationtasks. FollowingNairetal.[56],wetrainamodelG (F (I ),F (I ),l)
θ φ 0 φ i
thattakesinaninitialimageI ,afutureimageI ,languagelandoutputsascorecorrespondingtoif
0 i
transitioningfromI toI completesthelanguagel. Wetrainthemodelundertheobjectivethat(1)
0 i
thescoreshouldincreaseoverthecourseofthevideo,and(2)thescoreshouldbehigherforcorrect
pairings of video/language than for incorrect pairings. Again we sample a video clip and paired
language[I ,I ,l]1:B,andthentrainforthisobjectivedirectlywithacontrastiveloss,thatis:
i j>i
(cid:88) eGθ(z 0 b,z j b >i ,lb)
L =− log (2)
language
b∈B
eGθ(z
0
b,z
j
b
>i
,lb)+eGθ(z
0
b,z
i
b,lb)+eGθ(z
0
(cid:54)=b,z
j
(cid:54)=
>
b
i
,lb)
whereagainz =F (I),andz(cid:54)=bisanegativeexamplesampledfromadifferentvideointhebatch
φ
(thatdoesnotmatchthelanguageinstructionlb).
Regularization. Finally,wehypothesizethatsparseandcompactrepresentationsbenefitcontrol,
particularly in low data imitation learning. State-distribution shift is a well studied failure mode
in imitation learning [68], where policies trained with behavior cloning drift off the expert state
distribution. Reducingtheeffectivedimensionalityofthestatespace(whichweimplementwitha
simpleL1andL2penalty)canhelpmitigatethisissue,aswedemonstrateinSection4.4.
R3MSummary&Implementation. ThefinalobjectivefortrainingR3Mistheweightedsum:
L(φ,θ)=E [λ L +λ L +λ ||F (I )|| +λ ||F (I )|| ] (3)
I1:B ∼D 1 tcn 2 language 3 φ i 1 4 φ i 2
0,i,j,k
Inprinciple,R3McanbeimplementedontopofanyencodingarchitectureforF .Inourexperiments
φ
we focus on the ResNet50 architecture, and we release pre-trained R3M models with ResNet18,
ResNet34, and ResNet50 architectures [69], as well as the accompanying training code. During
training,φandθaretrainedwithanAdamoptimizertominimizeEquation3. Lastly,R3Malsotrains
withrandomcropping,appliedatthevideolevel(thatis,withinabatchallframesfromthesame
videoarecroppedidentically). Pleaseseetheappendixforfurtherimplementationdetails.
4 Experiments
In our experiments, we aim to study how the pre-trained R3M representation can be re-used for
multiple downstream robot learning tasks. First, we study if R3M enables more data efficient
imitationlearningonunseenenvironmentsandtaskscomparedtoexistingvisualrepresentationsand
learningfromscratch. Second,againinthedataefficientimitationlearningsetting,weablatethe
differentcomponentsoftheR3Mtrainingobjectiveandobservethatallcomponentsareimportantfor
finalperformance. Third,westudyifR3Mcanenableefficientrealrobotlearninginavisuallyrich
householdsetting. Finally,intheappendix,wetakeadeeperlookattaskperformanceofR3Mand
priormethodswithdifferentamountsofdata,differentcameraviewpoints,anddifferenttasks.
4.1 ImitationLearningEvaluationFramework
OurevaluationmethodologyislooselyinspiredbyParisietal.[23]. Wefocusonevaluatingvisual
representationsasfrozenperceptionmodulesfordownstreampolicylearningwithbehaviorcloning.
GivenapretrainedvisualrepresentationF ,weformthestaterepresentationasaconcatenationof
φ
thevisualembeddingz =F (I )andtherobotproprioceptive(e.g. jointpositionsandvelocities)
t φ t
readingp . Thepolicy,π,istrainedwithastandardbehaviorcloningloss||a −π([z ,p ])||2. We
t t t t 2
parameterizeπasatwo-layerMLPprecededbyaBatchNormattheinput. Wetraintheagentfor
20,000steps,evaluateitonlineintheenvironmentevery1000steps,andreportthebestsuccessrate
achieved. Foreachvisualrepresentationandeachtask,werun3seedsofbehaviorcloning. Thefinal
successratereportedonataskistheaverageovermultipleseeds,viewpoints,anddemodatasetsizes.
ComparisonsandBaselines. WecompareourR3Mmodeltothreeexistingvisualrepresentations
that have been shown to be effective for control: CLIP [12] which trains image representations
tobealignedwithpairednaturallanguagethroughcontrastivelearningandhasbeenshowntobe
usefulforsomemanipulation[36]andnavigationtasks[37],ImNetSupervisedwhichusesfeatures
5

--- Page 6 ---
Adroit
MetaWorld
Re-orient Pen, MetaWorld Franka Kitchen Adroit
Assembly, Bin Picking, Button Pressing, Drawer Opening, Hammering Relocate Ball
View 1 View 1
View 1
View 2 View 2
Franka Kitchen View 3 View 2 View 3
Sliding Door, Turning Light On, Opening Door, Turning Knob, Opening Microwave
Figure3: SimulatedEvaluationEnvironments.Weconsideracomprehensivesetofmanipulationtasksin
simulation(left),including5taskswithaSawyerfromMetaWorld[22],5tasksfromaFrankaoperatingovera
Kitchen[21],and2dexterousmanipulationtasksfromAdroit[20],withmultipleviewsperenvironment(right).
pre-trainedforImageNetclassificationtask[2]andhasbeenshowntobeeffectiveforreinforcement
learning[38],andMoCo(345)(PVR)[23],whichcompressesandfusesthethird,fourth,andfifth
convolutionallayersofaResNet-50modeltrainedwithMoCo[24]onImageNet,andhasbeenshown
tobeeffectiveforimitationlearning[23]. WenoteherethatourusageoftheMoco(345)model
differsfromthesetupinParisietal.[23]inaspectslikepropreoceptionfeatures,framestackingetc.
Asaresult,thenumericalresultsarenotdirectlycomparableacrossthetwoworks. Atthesametime,
weemphasizethatallvisualrepresentationsareusedinthesamewaywithinourevaluationprotocol.
4.2 SimulationEnvironments
Next,wedescribetheenvironmentsandtasksusedinourevaluations.Foracomprehensiveevaluation,
weusethreerobotmanipulationdomains: MetaWorld[22],theFrankaKitchenenvironment[21],
andAdroit[20](SeeFigure 3). Notetheseenvironmentsareonlyusedfordownstreamlearning,and
theseenvironmentsandtasksareneverseenduringR3Mtraining. IntheMetaWorldenvironment
weconsiderthetasksofassemblingaringontoapeg,pickingandplacingablockbetweenbins,
pushingabutton,openingadrawer,andhammeringanail. InFrankaKitchen,welearnthetasksof
slidingtherightdooropen,openingtheleftdoor,turningonthelight,turningthestovetopknob,
andopeningthemicrowave. Finally,inAdroitweconsiderthetasksofreorientingthepentothe
specifiedposition,andpickingandmovingtheballtospecifiedposition. Inalltasks,theagentis
providedwithimageobservations, aswellasproprioceptivedataoftherobot(end-effectorpose,
jointpositions,etc.) thatisconcatenatedtotheencodedimage. Alltasksinvolvevariation,either
by varying the position of the target object in MetaWorld, the positioning of the desk in Franka
Kitchen,orthechosengoalsinAdroit. Forarobustevaluation,weconsidermultipleviewsforeach
environment(SeeFigure3),and3datasetsizes: [5,10,25]inMetaWorldandFrankaKitchen,and
[25,50,100]inthemorechallengingAdroitenvironments. Ourcomparisonsmeasureperformance
foreachenvironmentandtask,averagedoverview,datasetsize,andobjectorgoalpositions.
4.3 Exp. 1: DoesR3Menableefficientimitationonunseenenvironmentsandtasks?
Inthisfirstexperiment,wemeasurethesuccessrateofdownstreamimitationlearningusingdifferent
visualrepresentations. InFigure4,wefirstnoticethatR3Misoverallabletolearnthesevisionbased
manipulationtasksinanextremelylowdataregimewith≈62%successrate,despiteneverseeingany
datafromthetargetenvironmentsintrainingtherepresentation,whileoutperforminglearningfrom
scratchbymorethan20%. Moreover,weobservethatR3Moutperformsallpriorrepresentations
bymorethan10%onaverageacrossall12tasks. Bytrainingondiverseinteractivevideodata,and
withobjectivesthatcapturetemporalstructureandlanguagerelevance,R3Misthebestperforming
methodinall3environments,andon11/12ofthetasks(Seeappendixforperformancebreakdownby
task). ThebesttwoperformingcomparisonsareCLIPandMoCo(345)(PVR),withCLIPperforming
better on MetaWorld, and MoCo (345) (PVR) performing better on Franka Kitchen and Adroit.
Unsurprisingly,learningfromscratchperformspoorlyinthelow-dataregimewestudy. Ultimately,
weconcludethatpre-trainedvisualrepresentationsareessentialtogoodperformanceinthelow-data
imitationlearningregime,andusingR3Mwithdiversehumanvideodataisespeciallyeffectivefor
learningrepresentationsusefulforroboticmanipulation.
6

--- Page 7 ---
Franka Kitchen MetaWorld Adroit
etaR
sseccuS
All Domains
Figure4: DataEfficientImitationLearninginUnseenEnvironments/Tasks. Wereportthesuccessrates
ofdownstreamimitationlearningwithstandarderrorbars.Weobservethatacross12tasksR3Moutperforms
baselineslikeMoCo(345)(PVR),CLIP,SupervisedImageNetfeatures,andtrainingfromscratch.
4.4 Exp. 2: WhichcomponentsofR3Mareimportant?
Inthisexperiment,weseek
Environment Supervised Self-Supervised
to understand the differ- R3M R3M(-Aug) R3M(-L1) R3M(-Lang)
ent components of R3M,
FrankaKitchen 53.1±2.7% 51.1±2.7% 46.7±2.7% 47.2±2.9%
beginning with the objec-
MetaWorld 69.2±2.0% 68.9±2.1% 65.0±2.4% 67.0±2.0%
tive. Specifically, wecom-
Adroit 65.0±1.7% 61.3±2.1% 66.5±1.6% 45.6±3.3%
pare the full R3M with
AllDomains 62.4±1.3% 60.4±1.4% 59.4±1.5% 53.2±1.5%
R3M(-Aug), which does
notusecropaugmentations, Table 1: Ablating Components of R3M. We see report success rate of
R3M(-L1),whichdoesnot downstreamimitationlearningonvariantsofR3M.Weobservethatonaverage,
include L1 regularization, removingtheL1penaltyhaveanegativeimpact,particularlyontheFranka
and R3M(-Lang), which KitchenandMetaWorldenvironments.Lastly,removinglanguagegrounding
hasthemostsignificantdropinperformance,particularlyontheAdroittasks.
doesnotincludeincludethe
video-languagealignmentloss. InTable1,wereportsuccessratesperenvironmentandaveraged
overallenvironments. First,wenoticethatonaverageacrossthethreeenvironments,weseeadrop
inperformanceof≈2%fromremovingcropaugmentationorfromremovingtheL1regularization.
Interestingly, theimpactofremovingthesparsityregularizationdependsontheenvironment. In
Franka Kitchen and MetaWorld, sparsity is helpful, while in Adroit removing sparsity actually
helps performance slightly. We suspect this is partly due to the Adroit environment using more
demonstrations,mitigatingthestatedistributionshiftissue.
Weseethatacrossallenvironments,removingvideo-languagealignmentlosshasthelargestnegative
impact on performance, particularly in the Adroit environment. We hypothesize that language
alignmentplaysanimportantroleinbettercapturingsemanticfeaturesthatmightbepredictiveof
objectsandusefulforobjectmanipulation.Nevertheless,wenotethateveninthefullyself-supervised
regime,ourR3MmodelstilloutperformspriorstateoftheartvisualrepresentationslikeImageNet
trainedMoCo(345)(PVR)[23]andCLIP[12]byasignificantmargin.
Franka Adroit
Next,weseektoanswerthequestion: Howimportantis
R3M 53.1(2.7) 65.0(1.7)
thedata? Todosoweincludecomparisonsthatdisentan-
MoCo-Ego4D 42.0(2.8) 54.9(2.7)
glestheroleofthedatasetandthetrainingobjective. In
MVP([70]) 27.0(2.6) 51.4(2.7)
particular, we have trained a MoCo model on the exact
sameframesoftheEgo4DdatasetusedtotrainourR3M Table 2: Importance of Data vs. Algo-
model(SeeTable2).AdditionallywecomparetotheMVP rithm. WefindthattheMoCo-Ego4Dand
MVP models, which leverage the same or
model [70], which trains a ViT-B masked auto-encoder
more data and compute as R3M perform
ontheEgo-soupdataset,whichcomprisesofEgo4Dand
morethan10%worse.
otheregocentricvideodatasets.. WeevaluatethesecomparisonsontheFrankaKitchenandAdroit
environments,andfindthattheMoCo-Ego4Dmodel,whichusesthesamedataandcomputeas
R3M,getsanaveragesuccessrate∼ 10%lowerthanR3Minbothenvironments. Moreover,
wefindtheMVPmodelsperforms∼20%worsethanR3M.Thissuggeststhatwhilethereisindeed
alargebenefitcomingfromdiversehumanvideodatacomparedtostaticImageNetimages(34%→
7

--- Page 8 ---
Putting
Lettuce
in Pan
Pushing
Mug to
Goal
Folding
Towel
Figure 5: RealWorldRobotLearningwithR3M.WithR3Mweareabletolearnchallengingtaskslike
puttinglettuceinthepan,pushingthecuptothegoal,andfoldingthetowelfromjust20demonstrations.See
appendixformoreexamplesofrealrobottasksanddetailsabouttherobotsetup.
42%onFranka),thedataisnottheonlysourceofimprovement,andtheR3Mobjectiveprovidesan
additional∼10%boostinsuccessrate.
4.5 Exp. 3: DoesR3Menabledataefficientlearninginrealworldenvironments?
Finally,wetestifR3Mcanenabledata-efficientrobotlearninginclutteredreal-worldenvironments.
To do so, we bring a Franka Emika Panda robot into a real graduate student apartment, and aim
to learn household tasks from pixels with just 20 demonstrations per task, using the pre-trained
R3Mrepresentation. Wehavetherobotcompletefivetasks: (1)closingadresserdrawer,(2)picking
afacemaskplacedrandomlyonadeskandplacingitinthedresserdrawer,(3)pickinguplettuce
randomlyplacedonacuttingboardandputtinginacookingpan,(4)pushingamugtoagoallocation,
and(5)foldingatowel(SeeFigure5). Likeinoursimulationexperiments,wecollectasmallnumber
ofdemonstrationsanddosimplebehaviorcloningwiththepre-trainedrepresentation.
InTable3,wereportthesuccessratescomparingR3Mand Successoutof10trials R3M CLIP
CLIP,oneofthestrongerbaselinesfromourevaluations
ClosingDrawer 80% 70%
insimulation. Weobservethatwhilethetwoperformsim-
PuttingMaskinDresser 30% 10%
ilarlyontheeasiertaskofclosingthedrawer,R3Mcon- PuttingLettuceinPan 60% 0%
sistentlyperformsbetterontheotherfourtasks(SeeFig- PushingMugtoGoal 70% 40%
ure5),whichrequiremoreprecisevisualrepresentations, FoldingTowel 40% 0%
yieldingnearlydoublethesuccessrateonaverage.
Average 56% 24%
5 LimitationsandFutureWork Table 3: Real World Success Rates.
R3MoutperformsCLIPonthechallenging
Inthiswork,wesetouttostudyifpre-trainingvisualrep- realworldmanipulationtasks.
resentationsondiversehumanvideoscanenableefficient
learningofdownstreamroboticmanipulationtasks. Whilewewereexcitedbystrongresultsona
widesetofsimulatedandrealrobotictasks,anumberofimportantlimitationsremain. Ourcurrent
evaluationislimitedtoimitationlearning,specificallybehaviorcloning,withasmallnumberoftask
demonstrations. WhilewewouldhopetoseeR3Mbeequallybeneficialforotherroboticlearning
settingslikereinforcementlearning,itcouldbethecasethatagoodpretrainedrepresentationforRL
isnotthesameasagoodpre-trainedrepresentationforimitation. StudyinghowR3MperformsinRL
settings,andchangesthatmayneedtomadetoimproveitsperformanceisanexcitingnextstep. The
currentR3Mmodelalsoonlyprovidesasingle-framestaterepresentation. Inprinciple,pre-training
onhumanvideosshouldbeabletogobeyondstaterepresentations(e.g. rewardlearningandtask
specification). StudyingifR3Membeddingsorthelanguagegroundingmodulecanprovideauseful
rewardsignalisaninterestingdirectionforfuturework.
8

--- Page 9 ---
Acknowledgments
The authors would like to thank the Ego4D team at Meta AI for assistance in using the dataset.
We’dalsoliketothankKarlPertsch,SimoneParisi,SiddKaramcheti,andnumerousmembersof
MetaAIandtheIRISlabsforvaluablediscussions. ThisworkisinpartsupportedbyONRgrant
N00014-22-1-2621. Finally,theauthorswouldalsoliketothankEvanColemanforassistancewith
therobot.
References
[1] S.Levine,C.Finn,T.Darrell,andP.Abbeel. End-to-endtrainingofdeepvisuomotorpolicies.
TheJournalofMachineLearningResearch,17(1):1334–1373,2016.
[2] J. Deng, W. Dong, R. Socher, L.-J. Li, K. Li, and L. Fei-Fei. ImageNet: A Large-Scale
HierarchicalImageDatabase. InCVPR09,2009.
[3] D. Mzurikwao, M. Khan, O. Samuel, J. Cinatl, M. Wass, M. Michaelis, G. Marcelli, and
C.S.Ang. Towardsimage-basedcancercelllinesauthenticationusingdeepneuralnetworks.
ScientificReports,10,112020. doi:10.1038/s41598-020-76670-6.
[4] J.Devlin,M.-W.Chang,K.Lee,andK.Toutanova. BERT:Pre-trainingofdeepbidirectional
transformersforlanguageunderstanding. InConferenceoftheNorthAmericanChapterof
theAssociationforComputationalLinguistics: HumanLanguageTechnologies(NAACL-HLT),
Minneapolis,Minnesota,June2019.AssociationforComputationalLinguistics.
[5] Z. Zhang, J. Liu, and N. Razavian. BERT-XML: Large scale automated ICD coding using
BERTpretraining. InProceedingsofthe3rdClinicalNaturalLanguageProcessingWorkshop,
pages24–34,Online,Nov.2020.AssociationforComputationalLinguistics. doi:10.18653/v1/
2020.clinicalnlp-1.3. URLhttps://aclanthology.org/2020.clinicalnlp-1.3.
[6] Z.Yang,N.Garcia,C.Chu,M.Otani,Y.Nakashima,andH.Takemura. Bertrepresentations
forvideoquestionanswering. In2020IEEEWinterConferenceonApplicationsofComputer
Vision(WACV),pages1545–1554,2020. doi:10.1109/WACV45572.2020.9093596.
[7] S.Dasari, F.Ebert, S.Tian, S.Nair, B.Bucher, K.Schmeckpeper, S.Singh, S.Levine, and
C.Finn. Robonet: Large-scalemulti-robotlearning. InConferenceonRobotLearning,2019.
[8] A. Mandlekar, J. Booher, M. Spero, A. Tung, A. Gupta, Y. Zhu, A. Garg, S. Savarese, and
L.Fei-Fei. Scalingrobotsupervisiontohundredsofhourswithroboturk: Roboticmanipulation
datasetthroughhumanreasoninganddexterity. In2019IEEE/RSJInternationalConferenceon
IntelligentRobotsandSystems(IROS),pages1048–1055.IEEE,2019.
[9] S.Young,D.Gandhi,S.Tulsiani,A.Gupta,P.Abbeel,andL.Pinto. Visualimitationmade
easy. InCoRL,2020.
[10] F. Ebert, Y. Yang, K. Schmeckpeper, B. Bucher, G. Georgakis, K. Daniilidis, C. Finn, and
S.Levine. Bridgedata: Boostinggeneralizationofroboticskillswithcross-domaindatasets.
ArXiv,abs/2109.13396,2021.
[11] T.B.Brownetal. Languagemodelsarefew-shotlearners. arXiv:2005.14165,2020.
[12] A. Radford, J. W. Kim, C. Hallacy, A. Ramesh, G. Goh, S. Agarwal, G. Sastry, A. Askell,
P.Mishkin,J.Clark,G.Krueger,andI.Sutskever. Learningtransferablevisualmodelsfrom
naturallanguagesupervision. InICML,2021.
[13] P.Goyal,Q.Duval,I.Seessel,M.Caron,I.Misra,L.Sagun,A.Joulin,andP.Bojanowski.Vision
models are more robust and fair when pretrained on uncurated images without supervision.
ArXiv,abs/2202.08360,2022.
9

--- Page 10 ---
[14] R.Goyal,S.EbrahimiKahou,V.Michalski,J.Materzynska,S.Westphal,H.Kim,V.Haenel,
I.Fruend,P.Yianilos,M.Mueller-Freitag,etal. The”somethingsomething”videodatabase
forlearningandevaluatingvisualcommonsense. InProceedingsoftheIEEEInternational
ConferenceonComputerVision,pages5842–5850,2017.
[15] D. Damen, H. Doughty, G. M. Farinella, S. Fidler, A. Furnari, E. Kazakos, D. Moltisanti,
J. Munro, T. Perrett, W. Price, and M. Wray. Scaling egocentric vision: The epic-kitchens
dataset. InEuropeanConferenceonComputerVision(ECCV),2018.
[16] K.Graumanetal. Ego4D:AroundtheWorldin3,000HoursofEgocentricVideo,2021.
[17] L.Shao,T.Migimatsu,Q.Zhang,K.Yang,andJ.Bohg. Concept2robot:Learningmanipulation
conceptsfrominstructionsandhumandemonstrations. InProceedingsofRobotics: Science
andSystems(RSS),2020.
[18] A. S. Chen, S. Nair, and C. Finn. Learning generalizable robotic reward functions from
”in-the-wild”humanvideos. ArXiv,abs/2103.16817,2021.
[19] P.Sermanet,C.Lynch,Y.Chebotar,J.Hsu,E.Jang,S.Schaal,andS.Levine. Time-contrastive
networks: Self-supervisedlearningfromvideo. ProceedingsofInternationalConferencein
RoboticsandAutomation(ICRA),2018.
[20] A. Rajeswaran, V. Kumar, A. Gupta, J. Schulman, E. Todorov, and S. Levine. Learning
complexdexterousmanipulationwithdeepreinforcementlearninganddemonstrations. ArXiv,
abs/1709.10087,2018.
[21] A.Gupta,V.Kumar,C.Lynch,S.Levine,andK.Hausman. Relaypolicylearning: Solving
long-horizontasksviaimitationandreinforcementlearning. InCoRL,2019.
[22] T. Yu, D. Quillen, Z. He, R. Julian, K. Hausman, C. Finn, and S. Levine. Meta-world: A
benchmarkandevaluationformulti-taskandmetareinforcementlearning. InConferenceon
RobotLearning,2020.
[23] S.Parisi,A.Rajeswaran,S.Purushwalkam,andA.K.Gupta. Theunsurprisingeffectivenessof
pre-trainedvisionmodelsforcontrol. 2022.
[24] K. He, H. Fan, Y. Wu, S. Xie, and R. B. Girshick. Momentum contrast for unsupervised
visualrepresentationlearning. 2020IEEE/CVFConferenceonComputerVisionandPattern
Recognition(CVPR),pages9726–9735,2020.
[25] M.Laskin,K.Lee,A.Stooke,L.Pinto,P.Abbeel,andA.Srinivas. Reinforcementlearning
withaugmenteddata. ArXiv,abs/2004.14990,2020.
[26] A. Srinivas, M. Laskin, and P. Abbeel. Curl: Contrastive unsupervised representations for
reinforcementlearning. InICML,2020.
[27] I.Kostrikov,D.Yarats,andR.Fergus. Imageaugmentationisallyouneed: Regularizingdeep
reinforcementlearningfrompixels. ArXiv,abs/2004.13649,2021.
[28] J.Pari,N.M.M.Shafiullah,S.P.Arunachalam,andL.Pinto. Thesurprisingeffectivenessof
representationlearningforvisualimitation. ArXiv,abs/2112.01511,2021.
[29] C.Gelada, S.Kumar,J.Buckman,O.Nachum, andM.G.Bellemare. Deepmdp: Learning
continuouslatentspacemodelsforrepresentationlearning. ArXiv,abs/1906.02736,2019.
[30] D.Hafner,T.P.Lillicrap,J.Ba,andM.Norouzi. Dreamtocontrol: Learningbehaviorsby
latentimagination. ArXiv,abs/1912.01603,2020.
[31] A.Zhang,R.McAllister,R.Calandra,Y.Gal,andS.Levine. Learninginvariantrepresentations
forreinforcementlearningwithoutreconstruction. ArXiv,abs/2006.10742,2021.
10

--- Page 11 ---
[32] S. Nair, S. Savarese, and C. Finn. Goal-aware prediction: Learning to model what matters.
ArXiv,abs/2007.07170,2020.
[33] M.Hong,K.Lee,M.Kang,W.Jung,andS.Oh. Dynamics-awaremetricembedding: Metric
learninginalatentspaceforvisualplanning. IEEERoboticsandAutomationLetters,2022.
[34] R.JonschkowskiandO.Brock. Learningstaterepresentationswithroboticpriors. Autonomous
Robots,39:407–428,102015. doi:10.1007/s10514-015-9459-7.
[35] Y.-C.Lin, A.Zeng, S.Song, P.Isola, andT.-Y.Lin. Learningtoseebeforelearningtoact:
Visualpre-trainingformanipulation. 2020IEEEInternationalConferenceonRoboticsand
Automation(ICRA),pages7286–7293,2020.
[36] M.Shridhar,L.Manuelli,andD.Fox. Cliport: Whatandwherepathwaysforroboticmanipula-
tion. InCoRL,2021.
[37] A.Khandelwal,L.Weihs,R.Mottaghi,andA.Kembhavi.Simplebuteffective:Clipembeddings
forembodiedai. ArXiv,abs/2111.09888,2021.
[38] R. Shah and V. Kumar. Rrl: Resnet as representation for reinforcement learning. ArXiv,
abs/2107.03380,2021.
[39] Y.Seo,K.Lee,S.James,andP.Abbeel. Reinforcementlearningwithaction-freepre-training
fromvideos. ArXiv,abs/2203.13880,2022.
[40] T.Xiao,I.Radosavovic,T.Darrell,andJ.Malik. Maskedvisualpre-trainingformotorcontrol.
2022.
[41] Y.Liu,A.Gupta,P.Abbeel,andS.Levine. Imitationfromobservation: Learningtoimitate
behaviorsfromrawvideoviacontexttranslation. In2018IEEEInternationalConferenceon
RoboticsandAutomation(ICRA),pages1118–1125.IEEE,2018.
[42] P. Sharma, D. Pathak, and A. Gupta. Third-person visual imitation learning via decoupled
hierarchicalcontroller. InNeurIPS,2019.
[43] L.Smith,N.Dhawan,M.Zhang,P.Abbeel,andS.Levine. AVID:LearningMulti-StageTasks
viaPixel-LevelTranslationofHumanVideos. InProceedingsofRobotics:ScienceandSystems,
Corvalis,Oregon,USA,July2020.
[44] T.Yu,C.Finn,S.Dasari,A.Xie,T.Zhang,P.Abbeel,andS.Levine. One-shotimitationfrom
observinghumansviadomain-adaptivemeta-learning. InProceedingsofRobotics: Scienceand
Systems,Pittsburgh,Pennsylvania,June2018.
[45] K.Schmeckpeper,A.Xie,O.Rybkin,S.Tian,K.Daniilidis,S.Levine,andC.Finn. Learning
predictivemodelsfromobservationandinteraction. InECCV,2020.
[46] A. D. Edwards and C. L. Isbell. Perceptual values from observation. arXiv preprint
arXiv:1905.07861,2019.
[47] K.Schmeckpeper,O.Rybkin,K.Daniilidis,S.Levine,andC.Finn. Reinforcementlearning
withvideos: Combiningofflineobservationswithinteraction. InCoRL,2020.
[48] R.Scalise,J.Thomason,Y.Bisk,andS.Srinivasa. Improvingrobotsuccessdetectionusing
staticobjectdata. InProceedingsofthe2019IEEE/RSJInternationalConferenceonIntelligent
RobotsandSystems,2019.
[49] S.Pirk,M.Khansari,Y.Bai,C.Lynch,andP.Sermanet. Onlineobjectrepresentationswith
contrastivelearning,2019.
[50] H.Xiong,Q.Li,Y.-C.Chen,H.Bharadhwaj,S.Sinha,andA.Garg. Learningbywatching:
Physicalimitationofmanipulationskillsfromhumanvideos,2021.
11

--- Page 12 ---
[51] N. Das, S. Bechtle, T. Davchev, D. Jayaraman, A. Rai, and F. Meier. Model-based inverse
reinforcementlearningfromvisualdemonstrations,2021.
[52] K.Zakka,A.Zeng,P.Florence,J.Tompson,J.Bohg,andD.Dwibedi. Xirl: Cross-embodiment
inversereinforcementlearning,2021.
[53] S.Stepputtis,J.Campbell,M.Phielipp,S.Lee,C.Baral,andH.B.Amor.Language-conditioned
imitationlearningforrobotmanipulationtasks. ArXiv,abs/2010.12083,2020.
[54] C.LynchandP.Sermanet. Groundinglanguageinplay. ArXiv,abs/2005.07648,2020.
[55] Y.Cui,S.Niekum,A.Gupta,V.Kumar,andA.Rajeswaran. CanFoundationModelsPerform
Zero-ShotTaskSpecificationForRobotManipulation? InL4DC,2022.
[56] S.Nair,E.Mitchell,K.Chen,B.Ichter,S.Savarese,andC.Finn.Learninglanguage-conditioned
robotbehaviorfromofflinedataandcrowd-sourcedannotation. InCoRL,2021.
[57] L.PintoandA.Gupta. Supersizingself-supervision: Learningtograspfrom50ktriesand700
robothours. InIEEEinternationalconferenceonroboticsandautomation(ICRA),2016.
[58] P. Sharma, L. Mohan, L. Pinto, and A. K. Gupta. Multiple interactions made easy (mime):
Largescaledemonstrationsdataforimitation. InCoRL,2018.
[59] E.Jang,A.Irpan,M.Khansari,D.Kappler,F.Ebert,C.Lynch,S.Levine,andC.Finn. Bc-
z: Zero-shot task generalization with robotic imitation learning. In A. Faust, D. Hsu, and
G.Neumann,editors,Proceedingsofthe5thConferenceonRobotLearning,volume164of
ProceedingsofMachineLearningResearch,pages991–1002.PMLR,08–11Nov2022. URL
https://proceedings.mlr.press/v164/jang22a.html.
[60] X.WangandA.K.Gupta. Unsupervisedlearningofvisualrepresentationsusingvideos. 2015
IEEEInternationalConferenceonComputerVision(ICCV),pages2794–2802,2015.
[61] P.Sermanet,K.Xu,andS.Levine. Unsupervisedperceptualrewardsforimitationlearning.
ProceedingsofRobotics: ScienceandSystems(RSS),2017.
[62] X.Wang,A.Jabri,andA.A.Efros. Learningcorrespondencefromthecycle-consistencyof
time. 2019IEEE/CVFConferenceonComputerVisionandPatternRecognition(CVPR),pages
2561–2571,2019.
[63] A.Jabri,A.Owens,andA.A.Efros. Space-timecorrespondenceasacontrastiverandomwalk.
ArXiv,abs/2006.14613,2020.
[64] M.Goyal, S. Modi, R.Goyal, and S.Gupta. Humanhands asprobesfor interactive object
understanding. InComputerVisionandPatternRecognition(CVPR),2022.
[65] A.Miech,D.Zhukov,J.-B.Alayrac,M.Tapaswi,I.Laptev,andJ.Sivic. Howto100m: Learning
atext-videoembeddingbywatchinghundredmillionnarratedvideoclips. 2019IEEE/CVF
InternationalConferenceonComputerVision(ICCV),pages2630–2640,2019.
[66] H. Xu, G. Ghosh, P.-Y. Huang, D. Okhonko, A. Aghajanyan, and F. M. L. Z. C. Feichten-
hofer. Videoclip: Contrastive pre-training for zero-shot video-text understanding. ArXiv,
abs/2109.14084,2021.
[67] A.vandenOord,Y.Li,andO.Vinyals. Representationlearningwithcontrastivepredictive
coding. ArXiv,abs/1807.03748,2018.
[68] S. Ross, G. J. Gordon, and J. A. Bagnell. A reduction of imitation learning and structured
predictiontono-regretonlinelearning. InAISTATS,2011.
[69] K.He,X.Zhang,S.Ren,andJ.Sun. Deepresiduallearningforimagerecognition. 2016IEEE
ConferenceonComputerVisionandPatternRecognition(CVPR),pages770–778,2016.
12

--- Page 13 ---
[70] I.Radosavovic,T.Xiao,S.James,P.Abbeel,J.Malik,andT.Darrell. Real-worldrobotlearning
withmaskedvisualpre-training. CoRL,2022.
[71] V.Sanh,L.Debut,J.Chaumond,andT.Wolf. Distilbert,adistilledversionofbert: smaller,
faster,cheaperandlighter. ArXiv,abs/1910.01108,2019.
13

--- Page 14 ---
A R3MTrainingDetails
A.1 DataPreprocessing
TheEgo4Ddatasetconsistsofseveralhourlongvideoswithinacertainscene. Withineachscene,
therearemanysub-clips,eachwithanaturallanguageannotation. R3Mtrainswiththeseshorter
videoclipspairedwithlanguageannotations.
For faster training R3M parses each video clip into frames (Resized and cropped to 224x224)
and samples frames from a video clip individually. See the codebase for more details on the
implementationofsamplingthevideos.
A.2 TrainingArchitectureandHyper-Parameters
R3McaninprinciplebetrainedwithanyvisualencodingarchitectureforF . Wetrainwithoffthe
φ
shelfResNet18,34,and50[69],asimplementedbytorchvision.models.
Thelanguagepredictionheadisimplementedasan5layerMLPwithsizes[2*E +L,1024,1024,
1024,1024]andoutputascalarscore,whereE istheoutputdimensionofF andListheoutput
φ
dimensionoftheDistilBERT[71]sentenceencoder(768)fromHuggingFacetransformers.
DuringtrainingofR3M,weusebatchsizesof16videoclips(where5framesaresamplesfromeach
videoclip: aninitialimage,finalimage,andsequenceof3frames). Theinitialandfinalframesare
sampledfromthefirstandlast20%ofthevideoclip.
R3Mmodelsaretrainedforonemillionstepsinourexperiments,andfor1.5millionstepsinour
releasedmodels,withalearningrateof0.0001.
For the training objective in Equation 3, we use hyperparameters λ = 1,λ = 1,λ =
1 2 3
0.00001,λ =0.00001.
4
A.3 AdditionalImplementationDetails
Inpractice,weusemorethanonenegativevideoexampleintrainingEquations1and2. Insteadwe
use3negativeexamples,sampledfromdifferentvideosinthebatch.
AdditionallyintrainingforEquation2,weconsiderthefollowingpositivepairswithinasinglebatch
element: InitialandFinalFrames(I ,I ),(I ,I ),and(I ,I ),withcorrespondingnegatives
0 g 0 j>i 0 k>j
(I ,I ),(I ,I ),and(I ,I )respectively. Usingalargernumberofpositiveexamplesfromasingle
0 0 0 i 0 j
videoandmultiplenegativeexamplesfromdifferentvideosstabilizestraining.
A.4 ExampleUsage
UsingR3Missimple.Thecodebaseislocatedathttps://github.com/facebookresearch/r3m.
Simplyclonetherepoandinstallviapip install -e . ThenR3Mcanbeloadedbyrunning:
1 from r3m import load_r3m
2 r3m = load_r3m("resnet50") # resnet18, resnet34
3 r3m.eval()
B EvaluationDetails
B.1 SimulationEnvironments
Wefocusonthreesimulationenvironments: FrankaKitchen,MetaWorld,andAdroit.
FrankaKitchen. TheFrankaKitchenenvironmentsusedinthispaperaremodifiedfromtheoriginal
environment;specifically,weaddadditionalrandomizationtothescene. Werandomlychangethe
positionofthekitchenbetweenepisodes,makingthetasksignificantlymorechallengingbothin
perceptionandcontrol.
The5tasksintheFrankaKitcheninvolveopeningtheleftdoor,openingtheslidingdoor,turningon
thelight,turningtheknob,andopeningthemicrowave. AllFrankatasksincludeproprioceptivedata
14

--- Page 15 ---
Closing
Drawer
Putting
Mask in
Dresser
Putting
Lettuce
inPan
Pushing
Mug to
Goal
Folding
Towel
Figure 6: RealWorldRobotLearningwithR3M.WithR3Mweareabletolearnchallengingtaskslike
closingthedrawer,puttingthemaskinthedresser,puttinglettuceinthepan,pushingthecuptothegoal,and
foldingthetowelfromjust20demonstrations.
ofthearmjointpositionsandgripperpositions. ThehorizonforallFrankatasksis50steps,andour
imitationexperimentsuseeither5,10,or25demos.
MetaWorld.TheMetaWorldenvironmentsarethestandardV2ButtonPressing,BinPicking,Drawer
Opening,Hammer,andAssemblyenvironmentsavailableinMetaWorld[22]. Inalltasks,thetarget
object(drawer,peg,block,etc.) positionisrandomizedbetweenepisodes.
AllMetaWorldtasksincludeproprioceptivedataofthegripperendeffectorposeandgripperopen/-
close. ThehorizonforallMetaWorldtasksis500steps,andourimitationexperimentsuseeither5,
10,or25demos.
Adroit. WeusethestandardPenandRelocatetasksintheAdroithandmanipulationsuite. Thegoal
positionofthepenandthegoalpositionoftheballarerandomizedbetweenepisodes,andspecified
visually.
AllAdroittasksincludeproprioceptivedataofthehandjoints,andintheRelocatetaskalsoincludes
theglobalpositionofthehand. ThehorizonforthePentaskis100stepsandfortheRelocatetaskis
200steps. Ourimitationexperimentsuseeither25,50,or100demos.
B.2 RealWorldEnvironments
OurrealworldexperimentsinvolvebringingaFrankaEmikaPandarobotintoarealgraduatestudent
apartment. Thetasksinvolveputtinglettuceinapaninthekitchen,pushingamugtoagoalposition
onadiningtable,closingadrawer,puttingamaskinadrawer,andfoldingatowel(SeeFigure6).
Alltasksinvolverandomization(e.g. thetowel/lettuce/mug/maskpositionordrawerposition). The
initialstateofthegripperisalsorandomizedeachepisode.
15

--- Page 16 ---
Putting Pushing Putting
Folding Closing
Mask in Mug to Lettuce
Towel Drawer
Dresser Goal in Pan
Figure7: RealRobotCameraViewpoints.Cameraviewusedforlearningeachoftherealrobottasks.
TherobotobservationincludesRGBimagesfromaUSBwebcam,positioneddifferentlyforeach
task(SeeFigure7). Therobotendeffectorpositionisalsoconcatenatedwiththeimageembedding
duringimitationlearning.
B.3 DemoDataCollection
In the Franka Kitchen and Adroit tasks, expert data is generated by training a state based agent
withmodelfreeRL[20]. Thestatebasedtrajectoriesarethenreplayedandrenderedwithimage
observations.
IntheMetaWorldenvironment,aheuristicpolicyusingstateinformationisusedtogenerateexpert
data,whichisthenreplayedandrenderedwithimageobservations.
Ontherealrobot,demonstrationsarecollectedbyahumantele-operatorwithaPlayStationcontroller.
The control is applied directly in the end effector Cartesian space, and the demo trajectories are
directlysavedwithvisualobservations.
B.4 Comparisons
InallexperimentsallmodelsuseaResNet50basearchitecture.
CLIP:TheCLIPcomparisonusestheoftheshelfCLIPRN50modelavailableathttps://github.
com/openai/CLIP.
ImNet Supervised: This comparison uses the default ResNet architecture available from
torchvision.modelswithpretrained=True.
MoCo(345): Thiscomparisonusesapre-trainedMoComodelonImagenetwhichfusesthethird,
fourth,andfifthconvolutionallayersasproposedin[23].
NotethatourusageoftheMoco(345)modeldiffersfromthesetupinParisietal.[23]inaspects
likeproprioceptionfeatures,framestackingetc. Asaresult,thenumericalresultsarenotdirectly
comparableacrossthetwoworks.
Scratch: uses the default ResNet architecture available from torchvision.models with
pretrained=False. Additionally,itletsgradientsfromthebehaviorcloningMSElosspassinto
thevisualencoder.
MoCo-Ego4D:Thiscomparisonusesapre-trainedMoComodelonthesameddataasR3Mfromthe
Ego4Ddataset.
MVP:ThiscomparisonusesapretrainedMVP[40,70]model,whichtrainsanMAEwithaViT-B
architectureontheEgo-Soupdataset,whichconsistsofEgo4Dandotheregocentrichumanvideo
datasets.
B.5 BehaviorCloningHyperparameters
Thedownstreampolicyisa2layerMLPwithhiddensizes[256,256]precededbyaBatchNorm. The
inputtothepolicyistheconcatenatedvisualembeddingandproprioceptivedata,andtheoutputis
16

--- Page 17 ---
Franka
Kitchen MetaWorld Adroit
Franka
Kitchen
View 1
MetaWorld
View 2
Adroit
View 3
# Demonstrations
Figure8: Performanceoverdifferentviews/datasetsizes.WereportthesuccessrateofR3Mandbaseline
across each view (left) and dataset size (right). We see that the performance improvement from R3M is
consistentacrossallviews.Wealsoobservethatwhileabsoluteperformanceincreaseswithmoredemos,the
performanceimprovementfromR3Misconsistentacrossalldemosizes.
theaction. Thepolicyistrainedwithalearningrateof0.001,andabatchsizeof32for20000steps,
evaluatingevery1000.
C AdditionalResults
C.1 Howdoesperformancevaryacrossviewpointanddemodatasetsize?
Inournextexperiment,wetakeacloserlookatR3Mperformancecomparedtopriormethodsacross
viewpointsanddatasetsizes. InFigure8,weplottheaveragesuccessrateofeachmethodacross
eachdatasetsizeandviewpoint. WeobservethattheperformanceimprovementofR3Misconsistent
acrossallviewpoints,anditisthehighestperformingrepresentationinallcases. Interestingly,we
seethatthesamedoesnotholdamongstthepriormethods,wheretherankingbetweenMoCo(345)
andCLIPchangesbasedonthechosenviewpoint.
Additionally,wealsostudytheimpactofdatasetsizeforimitationlearning. Again,weobservethat
theperformanceimprovementfromR3Misconsistent, outperformingthebaselinesacrossevery
environmentanddemodatasetsize. WeobservethatintheFrankaKitchenandAdroitenvironments,
theperformancegainfromR3Mstaysconsistentwithincreaseindatasetsize,evenastheabsolute
performanceofallmethodsimproves. Overall,weclearlyobservethattheperformancebenefitof
R3Misnottiedtoaspecificviewpointordatasetsize.
C.2 PerformanceBreakdownByTask
InFigure9wereportthesuccessrateoneachtaskindividually. Noteeachsuccessrateforeach
methodisstilltheaverageover3views,3demosizes,and3seeds. Weobservethaton11/12tasks
R3Misthehighestperformingmethod.
17

--- Page 18 ---
MetaWorld
Assembly, Bin Picking, Button Pressing, Drawer Opening, Hammering
Adroit
Re-orient Pen,
Relocate Ball
Franka Kitchen
Sliding Door, Turning Light On, Opening Door, Turning Knob, Opening Microwave
Figure9: PertaskSuccessRate.WeobservethatR3Misthehighestperformingmethodon11/12tasks.
18