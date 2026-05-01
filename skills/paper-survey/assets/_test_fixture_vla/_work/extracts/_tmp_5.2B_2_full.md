--- Page 1 ---
π : a Vision-Language-Action Model with
0.5
Open-World Generalization
Physical Intelligence
KevinBlack,NoahBrown,JamesDarpinian,KaranDhabalia,DannyDriess,AdnanEsmail,MichaelEqui,
ChelseaFinn,NiccoloFusai,ManuelY.Galliker,DibyaGhosh,LachyGroom,KarolHausman,BrianIchter,
SzymonJakubczak,TimJones,LiyimingKe,DevinLeBlanc,SergeyLevine,AdrianLi-Bell,MohithMothukuri,
SurajNair,KarlPertsch,AllenZ.Ren,LucyXiaoyangShi,LauraSmith,JostTobiasSpringenberg,KyleStachowicz
JamesTanner,QuanVuong,HomerWalke,AnnaWalling,HaohuanWang,LiliYu,UryZhilinsky
https://pi.website/blog/pi05
Multimodal Data Robot Action Data
π Vision-Language-Action Policy
0.5
Subtask Commands Robot Action In-the-wild Mobile Robot
High-Level Low-Level Action Expert
Close the microwave Pick up the mitten Language  Shirt in basket Make bed
Instruction
Object Detection In-the-wild Static Robot
Deploy out-of-the-box in new homes
Coffee
Dress
Fold linen Item in drawer
Multimodal Web Data In-Lab Static Robot
Q: How many desks 
are in the 
image?

A: 12
Fold laundry Sweep table
Q: Detect and label 
all objects in 
the scene.
 General Robot Data
A: <loc0112>

<loc0234>...
Q: What kind of pie 
is on this 
plate?

A: Chocolate
Fig.1:Theπ0.5modeltransfersknowledgefromaheterogeneousrangeofdatasources,includingotherrobots,high-levelsubtaskprediction,verbalinstructions,
anddatafromtheweb,inordertoenablebroadgeneralizationacrossenvironmentsandobjects.π0.5 cancontrolamobilemanipulatortocleankitchensand
bedroomsinnewhomesthatwerenotpresentinthetrainingdata,performingcomplexmulti-stagebehaviorswithdurationsof10to15minutes.
Abstract—In order for robots to be useful, they must perform horizon and dexterous manipulation skills, such as cleaning a
practically relevant tasks in the real world, outside of the lab. kitchen or bedroom, in entirely new homes.
While vision-language-action (VLA) models have demonstrated
impressive results for end-to-end robot control, it remains an I. INTRODUCTION
open question how far such models can generalize in the wild.
Wedescribeπ ,anewmodelbasedonπ thatusesco-training Stuff your eyes with wonder... See the world. It’s more
0.5 0
on heterogeneous tasks to enable broad generalization. π uses fantastic than any dream made or paid for in factories.
0.5
data from multiple robots, high-level semantic prediction, web
Ray Bradbury, Fahrenheit 451
data, and other sources to enable broadly generalizable real-
world robotic manipulation. Our system uses a combination of
Open-world generalization represents one of the biggest
co-trainingandhybridmulti-modalexamplesthatcombineimage
observations, language commands, object detections, semantic open problems in physical intelligence: embodied systems
subtaskprediction, and low-levelactions.Our experimentsshow such as robotic arms, humanoids, and autonomous vehicles
that this kind of knowledge transfer is essential for effective only truly become useful when they can leave the lab and
generalization, and we demonstrate for the first time that an
handlethe diversesituations andunexpectedevents thatoccur
end-to-end learning-enabled robotic system can perform long-
in the real world. Learning-based systems offer a path to en-
5202
rpA
22
]GL.sc[
1v45061.4052:viXra

--- Page 2 ---
“close the cabinets” “put the items in the drawer” “wipe the spill” “place the dishes in the sink”
Fig.2:π0.5cleaninganewkitchen.Therobotistaskedwithcleaningakitcheninahomethatwasnotinthetrainingdata.Themodelisgivengeneraltasks
(closethecabinets,puttheitemsinthedrawer,wipethespill,andputthedishesinthesink),whichitperformsbybothpredictingsubtaskstoaccomplish
(e.g.,pickuptheplate)andemittinglow-levelactions.
abling broad generalization, particularly with recent advances Building on the π VLA, we propose to include a range of
0
thathaveenabledscalablelearningsystemsindomainsranging different data sources to create the π model (“pi oh five”),
0.5
fromnaturallanguageprocessing[79,21,10,78]tocomputer which can control mobile manipulators to perform a variety
vision[34,66,35,43].However,thediversityofsituationsthat ofhouseholdtaskseveninhomesthatwereneverseenduring
a robot might encounter in the real world requires more than training.π drawsonexperiencefrommanysources:inaddi-
0.5
just scale: we need to design training recipes that can provide tion to a medium-sized dataset collected directly with mobile
the breadth of knowledge that will allow robots to generalize manipulators in a variety of real homes (about 400 hours),
at many levels of abstraction. For example, if a mobile robot π uses data from other non-mobile robots, data of related
0.5
is asked to clean up a kitchen that it has never seen before, tasks collected under laboratory conditions, training examples
some behaviors generalize readily if they are well represented that require predicting “high-level” semantic tasks based on
in the data with a sufficient range of scenes and objects (e.g., robot observation, verbal language instructions provided to
picking up a knife or plate), others might require adapting or the robot by human supervisors, and a variety of multi-modal
modifying existing skills to use them in a new way or in a examples created from web data, such as image captioning,
new sequence, and yet others might require understanding the question answering, and object localization (see Figure 1).
semantics of the scene based on prior knowledge (e.g., which The overwhelming majority of training examples provided to
drawer to open, or which object on the counter is most likely π (97.6% during the first training phase) do not come from
0.5
tobeadryingrack).Howcanwestructureatrainingrecipefor mobile manipulators performing household tasks, but from
a robotic learning system that can enable this kind of flexible theseothersources,suchasotherrobotsordatafromtheweb.
generalization? Nonetheless, π is able to control mobile manipulators in
0.5
Apersoncandrawonalifetimeofexperiencetosynthesize entirelynewhomesnotseenduringtraining,performintricate
appropriate solutions to each of these challenges. Not all of tasks such as hanging up towels or making beds, and can
this experience is firsthand, and not all of it comes from rote carry out long-horizon manipulation skills 10 to 15 minutes
practice – for example, we might use facts that we were told inlength,cleaninganentirekitchenorbedroombasedononly
by others or read in a book, together with bits of insight from a high-level prompt.
othertaskswehaveperformedindifferentcontexts,combined The design of π follows a simple hierarchical archi-
0.5
with direct experience in the target domain. Analogously, we tecture: we first pre-train the model on the heterogeneous
might hypothesize that generalizable robotic learning systems mixture of training tasks, and then fine-tune it specifically for
must be able to transfer experience and knowledge from a mobile manipulation with both low-level action examples and
variety of information sources. Some of these sources are high-level “semantic” actions, which correspond to predicting
firsthand experience with direct relevance to the task at hand, subtask labels such as “pick up the cutting board” or “rear-
some require transfer from other robot embodiments, envi- range the pillow.” At runtime, during each step of inference,
ronments, or domains, and some represent entirely different the model first predicts the semantic subtask, inferring the
data types, such as verbal instructions, perceptual tasks based behavior that is appropriate to perform next based on the task
on web data, or prediction of high-level semantic commands. structure and the semantics of the scene, and then predicts
The heterogeneity of these different sources of data present the low-level robot action chunk based on this subtask. This
a major obstacle, but fortunately recent advances in vision- simple architecture provides both the ability to reason about
language-action (VLA) models provide us with a toolkit that long-horizon multi-stage tasks and the ability to leverage
canmakethispossible:bycastingdifferentmodalitiesintothe differentsourcesofknowledgeforthetwolevels:thelow-level
same sequence modeling framework, VLAs can be adapted to action inference procedure readily benefits from action data
train on robot data, language data, computer vision tasks, and collected by other robots, including simpler static robots in
combinations of the above. other environments, while the high-level inference procedure
In this paper, we leverage this observation to design a co- benefits from semantic examples from the web, high-level
training framework for VLAs that can utilize heterogeneous annotation prediction, and even verbal commands that can be
anddiverseknowledgesourcestoenablebroadgeneralization. provided to the robot by human “supervisors” that walk the

--- Page 3 ---
robotthroughcomplextasksstepbystep,instructingit(much sources include data from other (non-mobile) robots, high-
like how they might instruct a person) on the appropriate level semantic subtask prediction, and data from the web.
subtasks to perform to complete a complex task such as Non-robot data co-training. A number of prior works have
cleaning a room. We illustrate this design in Figure 1. soughttousediversenon-robotdatatoimprovethegeneraliza-
Our central contribution is a system for training a highly tionofrobotpolicies.Priormethodshaveexploredinitializing
generalizable VLA, π , together with a proof of concept visionencodersfromcomputervisiondatasets[85,58,57,18],
0.5
that generalization can emerge from this model when it is orleveragingoff-the-shelftaskplanners[38,48,73,81].VLA
trained on appropriately diverse data. We provide a detailed policies are typically initialized from a pre-trained vision-
empirical evaluation of both π ’s generalization capabilities language model, which has been exposed to large amounts
0.5
and the relevance of different co-training ingredients. To our of internet vision and language data [23, 92, 42]. Notably, the
knowledge, our work is the first to demonstrate an end-to-end VLA architecture is flexible and allows to map between input
learning-enabledroboticsystemthatcanperformlong-horizon and output sequences of multi-modal vision, language, and
and dexterous manipulation skills, such as cleaning a kitchen actiontokens.Assuch,VLAsbroadenthedesignspaceofpos-
or bedroom, in entirely new homes. Our experiments and sible transfer approaches beyond simple weight initialization,
comparisons further show that this is enabled by transferring by supporting the co-training of a single, unified architecture
knowledge from other robots, high-level semantic prediction, on not just robot action imitation data, but any dataset that
verballanguageinstructionfromhumansupervisors,webdata, interleaves one or multiple of the aforementioned modalities.
and other sources. Prior works have demonstrated that co-training VLAs with
datamixturesusedforVLMtraining[23,92,86]canimprove
their generalization ability, e.g., when interacting with new
II. RELATEDWORK
objects or unseen scene backgrounds. In this work, we go
Generalist robot manipulation policies. Recent works have beyond VLM data co-training and design a system for co-
demonstratedthatbroadeningthetrainingdatadistributionfor training VLAs with a broader set of robotics-relevant super-
robot manipulation policies from narrow, single-task datasets vision sources, including data from other robots, high-level
to diverse datasets that span many scenes and tasks [17, semanticsubtaskpredictions,andverballanguageinstructions.
25, 80, 63, 41, 6, 30, 67, 1] allows the resulting poli- While multitask training and co-training are not new ideas,
cies to not only solve a wider range of tasks out of the we show that the specific combination of data sources in our
box, but also improves their ability to generalize to new system enables mobile robots to perform complex and long-
scenes and tasks [9, 63, 62, 22]. Training such generalist horizon behaviors in entirely new environments. We believe
policies requires new modeling approaches that can handle that this level of generalization, particularly when accounting
the scale and diversity of datasets that often span hundreds for the complexity of the tasks, goes significantly beyond the
of different tasks and scenes. Vision-language-action models results demonstrated in prior works.
(VLAs)[23,92,42,8,83,90,55,45,3,75,64,76,84,7,37] Robot reasoning and planning with language.Anumberof
offer an appealing solution: by fine-tuning pre-trained vision- prior works have shown that augmenting end-to-end policies
language models for robot control, VLAs can leverage the with high-level reasoning can significantly improve perfor-
semantic knowledge acquired from web-scale pretraining and mance for long-horizon tasks [2, 36, 44, 74, 71, 4, 16, 11,
bring it to bear on the robotics problem. When combined 53, 88, 51, 59, 13, 70, 91, 65, 72, 47, 76, 89], particularly
with highly expressive action decoding mechanisms like flow when high-level subtask inference can benefit from large pre-
matching [8], diffusion [55, 84, 52], or advanced action trained LLMs and VLMs. Our method also uses a two-stage
tokenization schemes [64], VLAs can perform a wide range inferenceprocedure,wherewefirstinferahigh-levelsemantic
of complex manipulation tasks in the real world. However, subtask (e.g., “pick up the plate”), and then predict the action
despiteimpressivelanguagefollowingabilities,VLAsarestill based on this subtask. Many prior methods have employed
typically evaluated in environments that closely match their two separate models for this purpose, with a VLM predicting
training data. While some studies suggest that simple skills semanticstepsandaseparatelow-levelpolicyexecutingthose
like picking up objects or opening drawers can be made to steps [2, 71, 13, 24, 70, 72, 47]. Our method uses the same
generalize simply by collecting robot data in a broader set exact model for both high-level and low-level inference, in
of environments [14, 67, 28, 49, 64], it is challenging to a recipe that more closely resembles chain-of-thought [82]
applythesameapproachtomorecomplex,long-horizontasks or test-time compute [39] methods, though unlike embodied
like cleaning up a kitchen, where achieving broad coverage chain-of-thoughtmethods[88,46,61],thehigh-levelinference
of plausible scenarios via brute-force scaling of robot data process still runs at a lower frequency than low-level action
collection is infeasible. In our experiments, we evaluate π inference.
0.5
in entirely new scenes, such as new kitchens and bedrooms Robotic learning systems with open-world generalization.
that were not seen in training, showing that our VLA can Whilemostroboticlearningsystemsareevaluatedinenviron-
generalize to entirely new scenes by leveraging not only ments that closely match the training data, a number of prior
direct first-hand experience on the target mobile manipulator workshaveexploredbroaderopen-worldgeneralization.When
platform, but also information from other data sources. These the robot’s tasks are restricted to a more narrow set of basic

--- Page 4 ---
pre-training post-training & inference
language subtasks “put the plate in the sink”
discretized actions -17 12 34 142 -72 -135 continuous actions
subtask prediction
open vocabulary captions “a dog catches a frisbee” -1.7 1.25 3.14 1.42
bounding boxes 3 35 145 223 “pick up the pillow”
pre-tprraei-nterda iVnLeM
d VLM
 pre-trained VLA action expert

SigLSIiPg L(I4P0 0(M4)0 0+M )G e+m mGae m(m2aB )(2.6B) (300M)
“clean the kitchen” “clean the bedroom” “pick up the pillow”
“pick up the pillow”
high-level prompt low-level command
“caption the image” noise
“localize the gripper”
multimodal web &
task-specific prompts
robot data
Fig.3:Model overview.π0.5 istrainedintwostages.First,apre-trainingstagecombinesallofthedifferentdatasourcestoproduceaninitialVLAwith
discretetokens.Thisstageusesdatafromdiverseroboticplatforms,high-levelsemanticactionprediction,anddatafromtheweb.RoboticdatausestheFAST
action tokenizer to represent actions as discrete tokens [64]. Second, a post-training stage specializes the model for low-level and high-level inferences for
mobilemanipulation,leveragingthemosttask-relevantdata,includingverbalinstructionsfromhumansupervisors.Thisstageusesflowmatchingtorepresent
theactiondistribution,enablingefficientreal-timeinferenceandtheabilitytorepresentfine-grainedcontinuousactionsequences.Atinferencetime,themodel
firstinfersahigh-levelsubtask,andthenpredictstheactionsbasedonthissubtask.
primitives, such as picking up objects, methods that allow for input to output tokens. The weights of these models are
task-specific assumptions (e.g., grasp prediction, or incorpo- initializedfrompre-trainedvision-languagemodels.Byencod-
rating model-based planning and control) have been shown to ing policy inputs and outputs into tokenized representations,
generalizebroadly,eventoentirelynewhomes[40,20,60,56, the imitation learning problem described above can be cast
29]. However, such methods do not readily generalize to the as a simple next-token-prediction problem over a sequence
full range of possible tasks that a generalist robot might need of observation, instruction and action tokens, and we can
toperform.Morerecently,large-scaledatasetscollectedacross leverage the scalable tools of modern machine learning to
many domains [41, 68, 63, 67, 14, 49] have been shown to optimizeit.Inpractice,thechoiceoftokenizersforimageand
enablegeneralizationofsimplebutend-to-endlearnedtasksto text inputs follows those of modern vision-language models.
new environments [33, 31, 67, 69, 26, 49, 28, 64]. However, For actions, prior work has developed effective, compression-
the tasks in these demonstrations are still relatively simple, based tokenization approaches [64], which we use in this
typicallylessthanaminuteinlengthandoftenwithrelatively work during pretraining. A number of recent VLA models
lowsuccessrates.Weshowthatπ canperformlong,multi- have also proposed to represent the action distribution via
0.5
stage tasks, such as putting all of the dishes in the sink or diffusion [55, 84, 52] or flow matching [8], providing a
picking all of the clothing off the floor of a new bedroom, more expressive representation over continuous-valued action
while generalizing to entirely new homes. chunks. During the post-training phase of our model, we will
build on the design of the π model [8], which represents
0
III. PRELIMINARIES the action distribution via flow matching. In this design, the
tokens corresponding to actions receive the partially denoised
Vision-language-actionmodels(VLAs)aretypicallytrained
actions from the previous step of flow matching as input, and
via imitation learning on diverse robot demonstration
output the flow matching vector field. These tokens also use a
datasets D, by maximizing the log-likelihood of an action
differentsetofmodelweights,whichwerefertoasan“action
a (or, more generally, an action chunk a ) given an
t t:t+H
expert,” analogously to a mixture of experts architecture. This
observation o and a natural language task instruction ℓ:
t
max E log (cid:0) π (a |o ,ℓ) (cid:1) .Theobservation action expert can specialize to flow matching-based action
θ (at:t+H,ot,ℓ)∼D θ t:t+H t generation, and can be significantly smaller than the rest of
typically contains one or more images I1,...,In and propri-
t t the LLM backbone.
oceptive state q , which captures the position of the robot’s
t
joints. VLA architectures follow the design of modern lan-
guage and vision-language models, with modality-specific
IV. THEπ
0.5
MODELANDTRAININGRECIPE
tokenizers that map inputs and outputs to discrete (“hard”) or We provide an overview of the π model and training
0.5
continuous (“soft”) token representations, and a large, auto- recipe in Figure 3. The model weights are initialized from a
regressive transformer backbone that is trained to map from standardVLMtrainedondatafromtheweb,andtrainingthen

--- Page 5 ---
proceeds in two stages: a pre-training stage intended to adapt in LLMs, image patch, textual prompt, and continuous action
the model to diverse robotic tasks, and a post-training stage tokens use bidirectional attention.
intended to specialize it to mobile manipulation and equip it As we want our model to output both text (to answer ques-
with the mechanisms for efficient test-time inference. During tions about the scene or to output next tasks to accomplish)
pre-training, all tasks, including tasks with robot actions, are and actions (to act in the world), the output of f is split
represented with discrete tokens, which leads to simple, scal- into text token logits and action output tokens, respectively
able,andefficienttraining[64].Duringpost-training,weadapt (cid:0) yℓ ,ya (cid:1) . The first M correspond to text token logits that
1:M 1:H
themodeltoalsohaveanactionexpert,aswithπ 0 ,inorderto can be used to sample ℓˆand the later H tokens are produced
both represent actions with finer granularity and enable more by a separate action expert, as in π , and projected via a
0
compute-efficientinferenceforreal-timecontrol.Atinference- linear mapping to continuous outputs used to obtain a
t:t+H
time,themodelfirstproducesahigh-levelsubtaskfortherobot (see next section). Note that M+H ≤N, i.e., not all outputs
to perform and then, conditioned on this subtask, predicts the are associated with a loss. The robot proprioceptive state is
low-levelactionsviatheactionexpert.Wedescribethemodel discretizedandinputtothemodelastexttokens.Moredetails
architecture below, followed by a description of each of the about the architecture are in Appendix E.
phases and their corresponding training tasks.
B. Combining discrete & continuous action representations
A. The π architecture
0.5
Similarly to π , we use flow-matching [50] to predict con-
The π architecture can flexibly represent both action 0
0.5 tinuous actions in the final model. Given aτ,ω =τa +
chunk distributions and tokenized text outputs, with the latter t:t+H t:t+H
(1−τ)ω, ω ∼N(0,I), where τ ∈[0,1] is the flow matching
used both for co-training tasks (e.g., question-answering) and
time index, the model is trained to predict the flow vector
for outputting high-level subtask predictions during hierar-
field ω−a . However, as shown in [64], VLA training can be
chical inference. The distribution captured by the model can t
be written as π (a ,ℓˆ|o ,ℓ), where o = [I1,...,In,q ] much faster when actions are represented by discrete tokens,
θ t:t+H t t t t t particularly when using a tokenization scheme that is efficient
consists of the images from all of the cameras and the robot’s
forcompressingtheactionchunks(e.g.,FAST).Unfortunately,
configuration (joint angles, gripper pose, torso lift pose, and
such discrete representations are less well-suited for real-
basevelocity),ℓistheoveralltaskprompt(e.g.,“putawaythe
dishes”), ℓˆrepresents the model’s (tokenized) textual output, time inference, because they require expensive autoregressive
decoding for inference [64]. Therefore, an ideal model design
which could be either a predicted high-level subtask (e.g.,
wouldtrainondiscretizedactionsbutstillallowforuseofflow
“pickuptheplate”)ortheanswertoavision-languageprompt
matching to produce continuous actions at inference time.
in web data, and a is a predicted action chunk. We
t:t+H
Our model is therefore trained to predict actions both
decompose the distribution as
through autoregressive sampling of tokens (using the FAST
π (a ,ℓˆ|o ,ℓ)=π (a |o ,ℓˆ)π (ℓˆ|o ,ℓ), tokenizer)anditerativeintegrationoftheflowfield,combining
θ t:t+H t θ t:t+H t θ t
the best of both worlds. We use the attention matrix to ensure
where the action distribution does not depend on ℓ, only on ℓˆ. that the different action representations do not attend to each
Thus, high-level inference captures π θ (ℓˆ|o t ,ℓ), and low-level other. Our model is optimized to minimize the combined loss
inference captures π (a |o ,ℓˆ), with both distributions
represented by the sam θ e t m :t+ o H del. t E (cid:104) H (cid:0) x ,fℓ(o ,ℓ) (cid:1)
D,τ,ω 1:M θ t
mu T lt h i e mo m d o a d l e in l p c u o t rr t e o s k p e o n n s d x s 1: t N o a (w t e ra u n s s e fo t r h m e e t r er t m ha t t o t k a e k n es lo i o n se N ly +α (cid:13) (cid:13)ω−a t:t+H −f θ a(aτ t: , t ω +H ,o t ,ℓ) (cid:13) (cid:13) 2 (cid:105) , (1)
here, referring to both discretized and continuous inputs) and
produces a sequence of multimodal outputs y , which we where H(x ,yℓ ) is the cross entropy loss between the
(cid:0) 1 (cid:1) :N 1:M 1:M
can write as y =f x ,A(x ),ρ(x ) . Each x can text tokens and predicted logits (including the FAST encoded
1:N 1:N 1:N 1:N i
be a text token (xw ∈ N), an image patch (xI ∈ Rp×p×3), actiontokens),ya =fa(aτ,ω ,o ,ℓ)istheoutputfromthe
i i 1:H θ t:t+H t
or an intermediate denoising value of a robot action in flow (smaller) action expert, and α ∈ R is a trade-off parameter.
matching(xa ∈Rd).Theobservationso andℓformtheprefix This scheme enables us to first pre-train our model as a
i t
part of x . Depending on the token type, as indicated by standard VLM transformer model by mapping actions to text
1:N
ρ(x ), each token can be processed not only by a different tokens (α=0), and then add additional action expert weights
i
encoder, but also by different expert weights within the trans- predicting continuous action tokens in a non-autoregressive
former. For example, image patches are fed through a vision fashionforfastinferenceinapost-trainingstage.Wefindthat
encoder, and text tokens are embedded with an embedding following this procedure, which is further explained below,
matrix. Following π [8], we linearly project action tokens xa leads to stable pre-training and excellent language following
0 i
into the transformer embedding space and use separate expert abilities of the VLA model. At inference time we then use
weights in the transformer to process the action tokens. The standard autoregressive decoding for text tokens ℓˆ followed
attentionmatrixA(x )∈[0,1]N×N indicatesifatokencan by 10 denoising steps, conditioned on text tokens, to produce
1:N
attendtoanothertoken.Comparedtostandardcausalattention actions a .
t:t+H

--- Page 6 ---
Pre-training
Laboratory Diverse mobile manipulator High-level subtask Verbal instruction
cross-embodiment
Put cup in sink
How would you
Sort clean the bedroom?
drawer
Shirt in basket Spatula in holder Wipe plate
Bounding boxes:
<loc0405><loc0011><loc0911><loc0197>closet

Pack Subtask: move to closet
bottles Place pillow on bed
Hang dress Tissue on stand Dish in sink How would you
clean the kitchen?
Sweep
table
Bounding boxes:
<loc0571><loc0376><loc0815><loc0484>mitten

<loc0787><loc0346><loc1003><loc0490>drawer

Subtask: move left arm forward and pick up mitten
Fold Make bed
laundry
Diverse non-mobile manipulator Multi-modal web data
Bus Describe this region: Policy: put plate in sink

table <loc0470><loc0390><loc0605><loc0484>  Relabeled: put plate on rack
Front legs of elephant
Item in drawer Fold linen Tidy table
What kind of pie is this?

This is a delicious-looking pecan
pie. The image shows a classic pecan
pie with its characteristic dark
brown filling studded with pecans. Policy: push the top drawer

Open X-Embodiment Cabinet putaway Kettle on base Towel on oven handle Relabeled: pick up blue shirt
Post-training
Fig. 4: Examples from pre-training and post-training tasks. π0.5 is pre-trained on data from mobile manipulators (MM), non-mobile robots in diverse
environments (ME), and cross-embodiment data collected under laboratory conditions (CE), as well as high-level subtask prediction (HL), and multi-modal
webdata(WD).Inapost-trainingphase,weadditionallyuseverbalinstructions(VI),andomitthelaboratorycross-embodimentdata(CE)tofocusthemodel
onmobilemanipulationanddiverseenvironments.Thefiguredisplaysanexemplarysubsetofthetasksineachcategory.
C. Pre-training to our evaluation (e.g., putting dishes in a bin), while others
In the first training stage, π is trained with a broad range arenot(e.g.,grindingcoffeebeans).Thisdataincludessingle-
0.5
of robot and non-robot data, which we summarize below and arm and dual-arm manipulators, and both static and mobile
illustrateinFigure4.Itistrainedasastandardauto-regressive bases.Wealsoincludetheopen-sourceOXEdataset[15].This
transformer, performing next-token prediction of text, object dataset is an extended version of the dataset used by π 0 [8].
locations, and FAST encoded action tokens. High-Level subtask prediction (HL). Breaking down high-
Diverse Mobile Manipulator data (MM). We use about 400 leveltaskcommandssuchas“cleanthebedroom”intoshorter
hours of data of mobile manipulators performing household subtaskslike“adjusttheblanket”and“pickuppillow”,similar
tasks in about 100 different home environments, some of to chain-of-thought prompting for language models, can help
whichareshowninFigure7,usingtherobotsinSectionIV-E. a trained policy reason about the current scene and better
Thissliceofthetrainingsetisthemostdirectlyrelevanttoour determine the next action. For robot data in MM, ME, and
evaluationtasks,whichconsistofsimilarcleaningandtidying CE where the task involves multiple subtasks, we manually
tasks in new, unseen, home environments. annotatealldatawithsemanticdescriptionsofthesubtasksand
Diverse Multi-Environment non-mobile robot data (ME). train π 0.5 to jointly predict the subtask labels (as text) as well
We also collected non-mobile robot data, either with a single as the actions (conditioned on the subtask label) based on the
arm or two arms, in a variety of home environments. These current observation and high-level command. This naturally
arms were fixed to surfaces or mounting platforms, and leads to a model that can act both as a high-level policy
because they are significantly lighter and easier to transport, (outputtingsubtasks)andlow-levelpolicythatexecutesactions
wewereabletogatheramorediversedatasetinawiderrange for these subtasks. We also label relevant bounding boxes
of homes with them. However, this ME data comes from a showninthecurrentobservationandtrainπ 0.5 topredictthem
different embodiment than the mobile robots. before predicting the subtask.
Cross-Embodimentlaboratorydata(CE).Wecollecteddata Multi-modal Web Data (WD). Finally we include a diverse
for a wide range of tasks (e.g., bussing a table, folding shirts) set of web data involving image captioning (CapsFusion [87],
in the laboratory, with simpler tabletop environments and a COCO [12]), question answering (Cambrian-7M [77], PixMo
variety of robot types. Some of these tasks are highly relevant [19],VQAv2[32]),andobjectlocalizationinpre-training.For

--- Page 7 ---
object localization, we further extend the standard datasets 4x images
front & rear camera
with additional web data of indoor scenes and household
objects with bounding box annotations.
For all action data, we train the model to predict target 2x 6 DoF arm + 1 DoF gripper
joint and end-effector poses. To differentiate the two, we add
‘<control mode> joint/end effector <control mode>’ to the 2x wrist camera
text prompt. All action data is normalized to [−1,1] using the
1%and99%quantileofeachactiondimensionoftheindivid-
ualdataset.Wesetthedimensionalityoftheactionatoafixed 1-2 DoF lift mechanism
numbertoaccommodatethelargestactionspaceamongallthe
datasets. For robots with lower-dimensional configuration and
3 DoF holonomic base
action spaces, we zero-pad the action vectors.
D. Post-training Fig. 5: Robot system overview. We use two mobile manipulator platforms
– each has four cameras (forward, backward, and both wrists), two 6 DoF
After pre-training the model with discrete tokens for 280k
arms with parallel jaw grippers, a mobile base, and a torso lift mechanism.
gradient steps, we perform a second stage of training that we The π0.5 model controls the joints and grippers of each arm, base velocity,
refer to as post-training. The purpose of this stage is to both andtheliftposition,resultingin18-19DoFstateandactionspaces.
specialize the model to our use-case (mobile manipulation
in homes), and to add an action expert that can produce
The control system is very simple: the π model directly
continuousactionchunksviaflowmatching.Thisstagejointly 0.5
commands target poses for the arms, gripper, and torso lift,
trains with next-token prediction, to preserve text prediction
andthetargetbasevelocitiesat50Hz(withactionchunking).
capabilities, and flow matching for the action expert (which
These targets are tracked with simple PD controllers, without
is initialized with random weights at the beginning of post-
any additional trajectory planning or collision detection. All
training). We optimize the objective in Equation (1), with
manipulation and navigation control is fully end-to-end.
α = 10.0 for 80k additional steps. The post-training action
dataset consists of the MM and ME robot data, filtered
V. EXPERIMENTALEVALUATION
down to successful episodes that are below a fixed length
The π model is designed to generalize broadly to new
threshold. We include web data (WD) to preserve the model’s 0.5
environments. While it is common to evaluate VLAs in
semantic and visual capabilities, and the slice of HL data
environments that match the training data, we conduct all of
correspondingtothemulti-environmentdatasets.Additionally,
our experiments in novel environments that were not seen in
toimprovethemodel’sabilitytopredictappropriatehigh-level
training. For quantitative comparisons, we use a set of mock
subtasks, we collect verbal instruction demonstrations (VI),
home environments to provide a controlled and reproducible
which are constructed by expert users providing “language
setup, while the most realistic final evaluation is conducted in
demonstrations,” selecting appropriate sub-task commands to
three real homes that were not part of the training set (see
commandtherobottoperformmobilemanipulationtasksstep
Figure 6). Our experiments focus on the following questions:
by step. These examples are collected by “teleoperating” the
robot in real time with language to perform tasks with the 1) Can π 0.5 effectively generalize to complex multi-stage
learned low level policy, essentially providing demonstrations tasks in entirely new homes?
of good high-level subtask outputs for a trained policy. 2) How does the generalization of π 0.5 scale with the
number of distinct environments in the training data?
E. Robot system details 3) Howdotheindividualco-trainingingredientsintheπ
0.5
The robot systems used in our mobile manipulation exper- training mixture contribute to its final performance?
iments are illustrated in Figure 5. We conducted all of our 4) How does π 0.5 compare to the π 0 VLA?
experiments using two types of mobile manipulators. Both 5) Howimportantisthehigh-levelinferencecomponentof
platforms are equipped with two 6 DoF arms with parallel π 0.5 ,andhowdoesitcomparetoflat,low-levelinference
jaw grippers and wrist-mounted monocular RGB cameras, a as well as oracle high-level baselines?
wheeled holonomic base, and a torso lift mechanism. The
A. Can π generalize to real homes?
state and action spaces for the base correspond to linear (2D) 0.5
and angular (1D) velocity, and the torso lift mechanism is To answer Question (1), we evaluated π in three real
0.5
either 1D (up/down) or 2D (up/down and forward/backward). homes that were not present in the training set, using both
Inadditiontothetwowristcameras,therobotshaveaforward types of robots. In each of the homes, the robots were in-
and backward facing camera mounted between the arms. We structed to perform a bedroom and kitchen cleaning task. The
use all four cameras for high-level inference, and the wrist evaluation rubrics for each task are provided in Appendix B
and forward cameras for the low-level inference process. The androughlycorrespondtothepercentageofstepsineachtask
total dimensionality of the state and action spaces is 18 or 19, that were completed successfully (e.g., placing half the dishes
depending on the platform. inthesinkcorrespondstoaround50%).TheresultsinFigure7

--- Page 8 ---
Mock Kitchens Real Kitchens
Mock Bedrooms Real Bedrooms
Fig.6:Evaluationenvironments.Weevaluateπ0.5inentirelynewkitchensandbedroomsthatwerenotseenduringtraining,withnovelobjects,backgrounds,
andlayouts.Weuseasetofmockroomsforcontrolled,reproduciblequantitativecomparisons(left)andrealhomesforarealisticfinalevaluation(right).
Home 1
Human: “put the
items in the drawer”
HL prediction: pull out the pull out the top pick up tong put tong into push the top
drawer right drawer drawer drawer
Home 2
Human: “place the
dishes in the sink”
HL prediction: pick up plate put plate in the put cup in the pick up the spoon pick up bowl
sink sink
Home 3
Human: “put the
laundry in the
laundry basket”
HL prediction: pick up shirt pick up shirt put clothes in put the shirt in put clothes in
the laundry the laundry laundry basket
basket basket
(a)Examplerollouts.Wevisualizeanexemplaryπ0.5episodeforonetaskfromeachhome.Topto
bottom:puttingitemsinadrawerinHome1,followedbyputtingdishesinthesinkinHome2,and (b) Quantitative evaluation. We show the task progress per task and
puttingclothesinthelaundrybasketinHome3.Thehumaninstructionforeachisgivenontheleft, environmentaveragedover10trials.Wefindthatπ0.5’sperformanceinthe
andthehigh-levelsubtaskpredictionfromπ0.5isshownbeneatheachframeinblue. mockevaluationsetupsisrepresentativeofitsperformanceinrealhomes.
Fig.7:Evaluationinrealhomes.Weevaluatedπ0.5 inthreekitchensandthreebedroomsinrealhomesthatwerenotseenduringtraining.Weevaluatethe
tasks‘itemsindrawer’,‘laundrybasket’,and‘dishesinsink,’andfindπ0.5 tobesuccessfulatthesetasksinthesecompletelynew,realhomes.
show that π was able to consistently succeed on a variety compute-intensive, for these experiments we pre-train on the
0.5
of tasks in each home (we note that, additionally, the model mixture of robot action prediction data without mobile ma-
is capable of performing many more tasks than used in our nipulation data, and then compare models post-trained on
quantitative evaluation). Many of the tasks involve multiple datasets that comprise mobile manipulation data from varying
stages (e.g., moving multiple objects) lasting about 2 to 5 numbers of environments. While the datasets split by location
minutes. For these trials, the model is provided with a simple in principle differ in size, in practice the number of training
high-level command (e.g., “place the dishes in the sink”), steps (40k) is chosen such that each model sees the same
andthehigh-levelinferenceprocessautonomouslydetermines number of unique data samples, which allows us to control
appropriate steps (e.g., “pick up the cup”). This level of in- for dataset size when varying the number of locations used
the-wild generalization goes significantly beyond the results within a post-training experiment.
demonstrated with prior vision-language-action models, both
Each model is evaluated in the mock environments shown
in terms of the degree of novelty that the model must handle,
in Figure 6, which are not seen in training. We conduct two
and the task duration and complexity.
types of evaluations. First, to evaluate overall performance on
multi-stage tasks, we use the standard rubric in Appendix B
B. How does generalization scale with the number of scenes?
and the mock test homes to evaluate each model’s end-to-end
In the next set of experiments, we aim to measure how performance on putting dishes in the sink, packing items into
generalization scales with the number of environments seen adrawer,puttingawaylaundry,andmakingabed.Second,we
in the training data. We vary the number of environments conductamorefine-grainedevaluationofeachmodel’sability
in the mobile manipulation data and measure its impact on tofollowlanguageinstructionsandinteractwithnovelobjects,
generalization by training with data from 3, 12, 22, 53, 82, where the robot must pick up specific objects from a kitchen
and 104 locations. Since applying the entire pre-training and counter based on language commands. These experiments
post-training recipe to each of these datasets is prohibitively use both in-distribution objects from similar categories as

--- Page 9 ---
Fig.9:Evaluatinglanguagefollowingwithdifferentnumbersoftraining
locations. We evaluate language following rate and success rate for picking
up user-indicated items and placing them into drawers or sinks, averaged
over seen object categories (“in-distribution”) or unseen categories (“out-of-
distribution”). Performance increases steadily as we increase the number of
Fig. 8: Evaluating performance with different numbers of locations. traininglocations.
Performanceoverthefourtesttasks—“dishesinsink”,“itemsindrawer”,
“laundrybasket”,“makebed”—improveswithmoretrainingenvironments.
The dashed green line and green bar show a baseline model that includes
the test homes in the training set. Compared to this model, our best model of locations in the training data increases, both language
achievessimilarperformance,despitenotseeinganydatafromthetesthomes. followingperformanceandsuccessrateimprove.Asexpected,
the performance on in-distribution objects improves more
quickly than that of out-of-distribution objects. As each new
those in the training data (but new instances), as well as environment introduces new household items, the model be-
out-of-distribution objects from unseen categories. The latter comes generally more robust and starts to generalize to task
necessitates broad semantic generalization. categories that were not present in the training data.
The results of the first experiment are shown in Figure 8.
C. How important is each part of our co-training recipe?
The average performance among the tasks generally improves
with more training locations. To quantify how much the final To study Question (3), we compare our full π 0.5 model
model (with 104 locations) bridges the generalization gap, we to other training mixtures to study the importance of each
include a control (shown in green) that is trained directly mixture component, again using end-to-end task performance
on data from the test homes. This control attains similar in the mock homes and the language following evaluation
performance as the final 104-location model, suggesting that described in Section V-B. As a reminder, our full recipe uses
ourco-trainingrecipeeffectivelyenablesbroadgeneralization, data from mobile manipulators in many environments (MM),
reaching similar performance to a model trained on the test static manipulators in many environments (ME), and diverse
environment. To confirm that this generalization performance cross-embodimentdatacollectedinlaboratorysettings(CE).It
requires our full co-training recipe, we additionally include alsoincludeshigh-leveldatawherethepredictioncorresponds
two baselines that do not use any of the other co-training to a high-level language command (HL), and web data corre-
tasks in the pre-training phase, but instead train directly on sponding to captioning, VQA, and object localization tasks
either data from the test environment (light green) or mobile (WD). Post-training also uses verbal instruction data (VI),
manipulation data from the 104 training locations (light yel- which we analyze in Section V-E. In these experiments, we
low).Theperformanceforboththosebaselinesissignificantly ablate different parts of the mixture:
worse—thisindicatesthattheotherdatasourcesleveragedby 1) no WD: this ablation excludes web data.
our full training recipe are essential for good generalization, 2) no ME: this ablation excludes multi-environment non-
even when the policy has seen robot data from test homes. mobile data.
When not using data from test homes, pre-training with our 3) no CE: this ablation excludes the laboratory cross-
recipe is especially important, as can be seen by the large gap embodiment data.
between the green bars and light yellow bar in Figure 8. 4) no ME or CE: this ablation excludes both data sources
The results of the second experiment (language following) fromotherrobots,suchthatthemodelistrainedononly
are shown in Figure 9. We report the language following datafromthetargetmobilemanipulatorplatformaswell
rate, which measures how often the robot selects the object as web data.
indicated in the language command, and success rate, which The results on the full mock home tasks are shown in
measures how often the robot successfully places that object Figure 10 (detailed breakdown of performance on each task
in the correct location (either inside the drawer or inside in Appendix D). First, we see in the results that excluding
the sink, depending on the test scenario). We separately either of the two cross-embodiment data sources (ME and
measure performance on object categories seen in training CE) significantly degrades performance, indicating that π
0.5
(but new object instances) and unseen (“out-of-distribution”) benefits considerably from cross-embodiment transfer, from
object categories. Details of this experiment are shown and bothotherenvironments(ME)andothertasks(CE).Excluding
discussed in Appendix C. Figure 9 shows that, as the number both sources harms performance even more. Interestingly, the

--- Page 10 ---
Fig. 12: Comparing π0.5 with other models. Our full model significantly
Fig. 10: Training recipe ablations, mock homes. We evaluate variants of outperformsbothπ0andπ0-FAST+Flowinthemockhometestenvironments.
ourmodelthatexcludedifferentpartsofthetrainingmixtureonallfourtest
tasks(10trialsperpolicyandtask).Includingcross-embodimentdata,bothin
diverseenvironments(ME)andfordiversetasksinlaboratorysettings(CE)is
only, without the HL or WD datasets. These models provide
importantforgoodperformance,withlargedegradationwheneitherorboth
ofthesedatasourcesareremoved.Webdata(WD)doesnotmakeasignificant a strong point of comparison, since π 0 has been demon-
differenceintheseexperiments,butwewillseeinFigures11and13thatit strated to perform strongly on complex and dexterous mobile
impactsobjectgeneralizationandhigh-levelperformance.
manipulation tasks, and the enhancement in π -FAST+Flow
0
brings it as close to π as possible. π builds on these
0.5 0.5
models with a combination of co-training tasks. For a fair
comparison, all models receive the same cross-embodiment
robot training set and are trained for a comparable number
of steps. The differences then are: (1) π additionally uses
0.5
HL and WD data; (2) π uses a hybrid training procedure,
0.5
with discrete tokenized training in the pre-training phase, and
training with a flow matching action expert only in the post-
training phase, while π always uses the action expert. π -
0 0
FAST+Flow follows the hybrid training recipe but is trained
only with data containing robot actions and thus cannot
perform high-level inference. The results in Figure 12 show
that π significantly outperforms both π and our enhanced
0.5 0
Fig.11:Trainingrecipeablations,languagefollowing.Evaluatinglanguage version. This result holds even when we allow for longer
followingwithin-distributionandout-of-distributionobjectsaftertrainingon
training up to 300k training steps of π , confirming that as in
differentnumbersoflocations.Includingwebdata(WD)isimportantforout- 0
of-distribution(OOD)performanceinparticular.Cross-embodiment(CE)and Pertschetal.[64]trainingwithFASTtokensismoreeffective
diverse environment (ME) data both have a large impact on in-distribution in terms of compute than pure diffusion based training.
andout-of-distributionperformance.
E. How important is high-level inference?
Finally, we evaluate the importance of high-level inference,
difference in performance with the no WD ablation is not
and compare the performance of several alternative high-level
statistically significant in this experiment, though we show
inference methods. The high-level inference mechanism in
later that web data has a large impact on language following
π takes in a high-level command (e.g., “clean the bed-
(below) and high-level subtask inference (Section V-E). 0.5
room”) and outputs the subtask to complete (e.g., “pick up
Theresultsofthelanguagefollowingexperiment,shownin
pillow”),whichisthenusedascontextforinferringthelower-
Figure 11, show a similar trend as Figure 10 — excluding
level actions, analogously to chain of thought inference [82].
ME or/and CE data leads to a significant degradation in
While π uses a unified architecture where the same model
performance. What differs now is that removing web data 0.5
performs both high-level and low-level inference, we can
(no WD) causes significantly worse performance on out-of-
also construct baseline methods that either forego the high-
distribution(OOD)objects—weconjecturethattrainingwith
level inference process and feed the task prompt directly
web data, which contains very broad knowledge of physical
into the low-level system, as is common in standard VLA
objects, allows the model to understand and follow language
models [92, 8], or use another model for high-level inference
commands involving unseen object categories.
to ablate the importance of different dataset components in
D. How does π 0.5 compare to other VLAs? termsoftheirimpactonthehigh-levelpolicy.Weconsiderthe
We compare π 0.5 to the original π 0 VLA as well as an followingmethodsandablations,allofwhichusethefullπ 0.5
improved version of π which we denote as π -FAST+Flow. low-level inference process with different high-level policies:
0 0
ThisversionistrainedviathejointdiffusionandFASTaction 1) π model for high-level and low-level inference.
0.5
prediction formulation from Equation (1), but on action data 2) no WD: an ablation of π that excludes web data.
0.5

--- Page 11 ---
high-levelpolicy.Finally,thezero-shotGPT-4ablationattains
the worst performance, indicating the importance of adapting
VLMs with robot data. We provide a detailed breakdown of
performance on each task in Appendix D, Figure 17.
VI. DISCUSSIONANDFUTUREWORK
We described π , a co-trained model that builds on the
0.5
π VLA to integrate a variety of data sources and enable
0
generalizationtonewenvironments.Theπ VLAcancontrol
0.5
mobilemanipulatorstoperformtasksinhomesthatwerenever
seen in the training data, cleaning kitchens and bedrooms,
making beds, hanging towels, and performing other multi-
stage and dexterous behaviors. π is trained on about 400
0.5
hours of mobile manipulation data, but includes a much
largeramountofdatafromotherrobots,includingnon-mobile
manipulatorsindiverseenvironmentsanddatacollectedunder
Fig. 13: Evaluation of the high-level inference process. While the full laboratory conditions. It is also co-trained jointly with data
π0.5 model with high-level and low-level inference attains the best results, from the web, as well as high-level prediction data for out-
usingonlylow-levelinference(“implicitHL”)withthefullπ0.5 modelalso
putting language commands based on robot observations. The
benefits from the inclusion of high-level subtask examples in training. In
contrast, excluding verbal instructions (no VI) or web data (no WD) leads generalization capabilities of π 0.5 demonstrate that this co-
toasignificantdegradationinperformance,andzero-shotpromptingalarge training recipe facilitates effective transfer, enabling highly
API-basedmodel(GPT-4)performsworse.
generalizable control of a mobile manipulator with only a
medium-sized mobile manipulation dataset.
π is not without its limitations. While our VLA ex-
0.5
3) no VI: an ablation of π that excludes the verbal
0.5 hibits broad generalization, it still makes mistakes. Some
instruction (VI) data.
environments present persistent challenges (e.g., unfamiliar
4) implicit HL: no high-level inference at runtime but
handles on drawers, or cabinets that are physically hard for
includes high-level data in training, which may teach
the robot to open), some behaviors present challenges with
the model about subtasks implicitly.
partial observability (e.g., the robot arm occluding a spill
5) no HL: no high-level inference, and no high-level data
that should be wiped), and in some cases the high-level sub-
in training at all.
task inference is easily distracted (e.g., closing and opening a
6) GPT-4: use GPT-4 as the high-level policy, evaluating
drawer multiple times while putting away items). Addressing
theimportanceoftrainingthehigh-levelpolicyonrobot
these challenges with better co-training, transfer, and larger
data. To align the model with our domain, we prompt
datasets is a promising direction for future work. Other future
GPT-4 with a description of the task and a list of the
work directions could address the technical constraints of our
most used labels to choose from.
method. While π can perform a variety of behaviors to
0.5
7) human HL: use an expert human as an “oracle” high-
cleanupkitchensandbedrooms,itprocessesrelativelysimple
levelpolicy,toprovideanupperboundonperformance.
prompts. The complexity of the prompts that the model can
The results of these experiments are shown in Figure 13. accommodate is determined by the training data, and more
The full π model performs the best, and outperforms even complex preferences and instructions could be incorporated
0.5
the human HL “oracle” baseline. Perhaps surprisingly, the by producing more intricate and diverse annotations, either
second best model is the implicit HL ablation, which does with human labelers or synthetically. The model also uses
not perform any high-level inference, but includes the full a relatively modest context, and incorporating richer context
data mixture, i.e. also subtask prediction, in training. This andmemorycouldmakethemodelsignificantlymorecapable
stronglysuggeststheimportanceoftheco-trainingrecipeused in settings with more partial observability, such as tasks that
by our model: while there is a benefit to explicitly infer high- require navigating between different rooms or remembering
level subtasks, a significant portion of that benefit is already where objects are stored. More broadly, π explores a
0.5
obtained simply by including subtask prediction data in the particular combination of heterogeneous data sources, but the
training mixture. The no HL ablation, excluding HL task specific sources of data can be explored even more broadly.
even in training, performs significantly worse. The results For instance, the ability of our system to learn from verbal
also show that the relatively small verbal instruction dataset, instructionsprovidesapowerfulnewsupervisionmodality,and
which only constitutes about 11% of the high-level mobile future work couldexplore this and other waysthat people can
manipulationexamples,iscriticaltostrongperformanceasthe providerobotswithadditionalcontextualknowledge.Wehope
no VI ablation is significantly weaker. The no WD ablation that our work will serve as a foundation for a new generation
is also significantly worse, indicating that much of the benefit ofVLAsthatexhibitbroadgeneralizationtodiversereal-world
of web data (perhaps unsurprisingly) lies in improving the environments.

--- Page 12 ---
ACKNOWLEDGEMENTS [7] Johan Bjorck, Fernando Castan˜eda, Nikita Cherniadev,
We thank our robot operators for data collection, evalua- XingyeDa,RunyuDing,LinxiFan,YuFang,DieterFox,
tions, logistics, and video recording. See Appendix A for a Fengyuan Hu, Spencer Huang, et al. Gr00t n1: An open
full contributions statement. foundation model for generalist humanoid robots. arXiv
preprint arXiv:2503.14734, 2025.
REFERENCES
[8] Kevin Black, Noah Brown, Danny Driess, Adnan Es-
[1] AgiBot-World-Contributors, Qingwen Bu, Jisong Cai, mail, Michael Equi, Chelsea Finn, Niccolo Fusai,
Li Chen, Xiuqi Cui, Yan Ding, Siyuan Feng, Shenyuan Lachy Groom, Karol Hausman, Brian Ichter, Szymon
Gao, Xindong He, Xuan Hu, Xu Huang, Shu Jiang, Jakubczak, Tim Jones, Liyiming Ke, Sergey Levine,
YuxinJiang,ChengJing,HongyangLi,JialuLi,Chiming Adrian Li-Bell, Mohith Mothukuri, Suraj Nair, Karl
Liu, Yi Liu, Yuxiang Lu, Jianlan Luo, Ping Luo, Yao Pertsch,LucyXiaoyangShi,JamesTanner,QuanVuong,
Mu,YuehanNiu,YixuanPan,JiangmiaoPang,YuQiao, Anna Walling, Haohuan Wang, and Ury Zhilinsky. π :
0
Guanghui Ren, Cheng Ruan, Jiaqi Shan, Yongjian Shen, A vision-language-action flow model for general robot
ChengshiShi,MingkangShi,ModiShi,ChonghaoSima, control. arXiv preprint arXiv:2410.24164, 2024.
Jianheng Song, Huijie Wang, Wenhao Wang, Dafeng [9] Anthony Brohan, Noah Brown, Justice Carbajal, Yev-
Wei, Chengen Xie, Guo Xu, Junchi Yan, Cunbiao Yang, gen Chebotar, Joseph Dabis, Chelsea Finn, Keerthana
Lei Yang, Shukai Yang, Maoqing Yao, Jia Zeng, Chi Gopalakrishnan, Karol Hausman, Alex Herzog, Jasmine
Zhang, Qinglin Zhang, Bin Zhao, Chengyue Zhao, Jiaqi Hsu, Julian Ibarz, Brian Ichter, Alex Irpan, Tomas
Zhao,andJianchaoZhu. Agibotworldcolosseo:Alarge- Jackson, Sally Jesmonth, Nikhil Joshi, Ryan Julian,
scale manipulation platform for scalable and intelligent DmitryKalashnikov,YuhengKuang,IsabelLeal,Kuang-
embodied systems. arXiv preprint arXiv:2503.06669, Huei Lee, Sergey Levine, Yao Lu, Utsav Malla, Deek-
2025. sha Manjunath, Igor Mordatch, Ofir Nachum, Carolina
[2] Michael Ahn, Anthony Brohan, Noah Brown, Yevgen Parada, Jodilyn Peralta, Emily Perez, Karl Pertsch, Jor-
Chebotar, Omar Cortes, Byron David, Chelsea Finn, nell Quiambao, Kanishka Rao, Michael Ryoo, Grecia
Chuyuan Fu, Keerthana Gopalakrishnan, Karol Haus- Salazar, Pannag Sanketi, Kevin Sayed, Jaspiar Singh,
man,AlexHerzog,DanielHo,JasmineHsu,JulianIbarz, Sumedh Sontakke, Austin Stone, Clayton Tan, Huong
Brian Ichter, Alex Irpan, Eric Jang, Rosario Jauregui Tran, Vincent Vanhoucke, Steve Vega, Quan Vuong, Fei
Ruano, Kyle Jeffrey, Sally Jesmonth, Nikhil Joshi, Ryan Xia,TedXiao,PengXu,SichunXu,TianheYu,andBri-
Julian,DmitryKalashnikov,YuhengKuang,Kuang-Huei annaZitkovich.Rt-1:Roboticstransformerforreal-world
Lee,SergeyLevine,YaoLu,LindaLuu,CarolinaParada, control at scale. In arXiv preprint arXiv:2212.06817,
PeterPastor,JornellQuiambao,KanishkaRao,JarekRet- 2022.
tinghouse, Diego Reyes, Pierre Sermanet, Nicolas Siev- [10] Tom B. Brown, Benjamin Mann, Nick Ryder, Melanie
ers,ClaytonTan,AlexanderToshev,VincentVanhoucke, Subbiah, Jared Kaplan, Prafulla Dhariwal, Arvind
Fei Xia, Ted Xiao, Peng Xu, Sichun Xu, Mengyuan Neelakantan, Pranav Shyam, Girish Sastry, Amanda
Yan, and Andy Zeng. Do as i can and not as i say: Askell, Sandhini Agarwal, Ariel Herbert-Voss, Gretchen
Grounding language in robotic affordances. In arXiv Krueger, Tom Henighan, Rewon Child, Aditya Ramesh,
preprint arXiv:2204.01691, 2022. DanielM.Ziegler,JeffWu,ClemensWinter,Christopher
[3] SuneelBelkhaleandDorsaSadigh. Minivla:Abettervla Hesse, Mark Chen, Eric Sigler, Mateusz Litwin, Scott
with a smaller footprint, 2024. URL https://github.com/ Gray, Benjamin Chess, Jack Clark, Christopher Berner,
Stanford-ILIAD/openvla-mini. Sam McCandlish, Alec Radford, Ilya Sutskever, and
[4] SuneelBelkhale,TianliDing,TedXiao,PierreSermanet, Dario Amodei. Language models are few-shot learners.
Quon Vuong, Jonathan Tompson, Yevgen Chebotar, De- In Advances in Neural Information Processing Systems,
bidatta Dwibedi, and Dorsa Sadigh. Rt-h: Action hier- 2020.
archies using language, 2024. URL https://arxiv.org/abs/ [11] HongyiChen,YunchaoYao,RuixuanLiu,ChangliuLiu,
2403.01823. andJeffreyIchnowski.Automatingrobotfailurerecovery
[5] Lucas Beyer, Andreas Steiner, Andre´ Susano Pinto, using vision-language models with optimized prompts.
Alexander Kolesnikov, Xiao Wang, Daniel Salz, Maxim arXiv preprint arXiv:2409.03966, 2024.
Neumann, Ibrahim Alabdulmohsin, Michael Tschannen, [12] Xinlei Chen, Hao Fang, Tsung-Yi Lin, Ramakrishna
Emanuele Bugliarello, et al. Paligemma: A versatile 3b Vedantam,SaurabhGupta,PiotrDolla´r,andCLawrence
vlmfortransfer. arXivpreprintarXiv:2407.07726,2024. Zitnick. Microsoft coco captions: Data collection and
[6] Homanga Bharadhwaj, Jay Vakil, Mohit Sharma, Ab- evaluation server. arXiv preprint arXiv:1504.00325,
hinav Gupta, Shubham Tulsiani, and Vikash Kumar. 2015.
Roboagent:Generalizationandefficiencyinrobotmanip- [13] An-Chieh Cheng, Yandong Ji, Zhaojing Yang, Zaitian
ulationviasemanticaugmentationsandactionchunking. Gongye, Xueyan Zou, Jan Kautz, Erdem Bıyık, Hongxu
In 2024 IEEE International Conference on Robotics and Yin, Sifei Liu, and Xiaolong Wang. Navila: Legged
Automation (ICRA), pages 4788–4795. IEEE, 2024. robotvision-language-actionmodelfornavigation. arXiv

--- Page 13 ---
preprint arXiv:2412.04453, 2024. Boosting generalization of robotic skills with cross-
[14] Cheng Chi, Zhenjia Xu, Chuer Pan, Eric Cousineau, domaindatasets. arXivpreprintarXiv:2109.13396,2021.
Benjamin Burchfiel, Siyuan Feng, Russ Tedrake, and [26] Kiana Ehsani, Tanmay Gupta, Rose Hendrix, Jordi Sal-
Shuran Song. Universal manipulation interface: In- vador, Luca Weihs, Kuo-Hao Zeng, Kunal Pratap Singh,
the-wild robot teaching without in-the-wild robots. In Yejin Kim, Winson Han, Alvaro Herrasti, et al. Spoc:
Proceedings of Robotics: Science and Systems (RSS), Imitating shortest paths in simulation enables effective
2024. navigation and manipulation in the real world. arXiv
[15] OX-Embodiment Collaboration, A Padalkar, A Pooley, preprint arXiv:2312.02976, 2023.
A Jain, A Bewley, A Herzog, A Irpan, A Khazatsky, [27] Patrick Esser, Sumith Kulal, Andreas Blattmann, Rahim
A Rai, A Singh, et al. Open X-Embodiment: Robotic Entezari, Jonas Mu¨ller, Harry Saini, Yam Levi, Dominik
learning datasets and RT-X models. arXiv preprint Lorenz, Axel Sauer, Frederic Boesel, et al. Scaling
arXiv:2310.08864, 1(2), 2023. rectified flow transformers for high-resolution image
[16] Yinpei Dai, Jayjun Lee, Nima Fazeli, and Joyce Chai. synthesis. In Forty-first International Conference on
Racer:Richlanguage-guidedfailurerecoverypoliciesfor Machine Learning, 2024.
imitationlearning. InternationalConferenceonRobotics [28] Haritheja Etukuru, Norihito Naka, Zijin Hu, Seung-
and Automation (ICRA), 2025. jae Lee, Julian Mehu, Aaron Edsinger, Chris Pax-
[17] SudeepDasari,FrederikEbert,StephenTian,SurajNair, ton, Soumith Chintala, Lerrel Pinto, and Nur Muham-
BernadetteBucher,KarlSchmeckpeper,SiddharthSingh, mad Mahi Shafiullah. Robot utility models: General
Sergey Levine, and Chelsea Finn. Robonet: Large-scale policies for zero-shot deployment in new environments.
multi-robot learning. CoRL, 2019. arXiv preprint arXiv:2409.05865, 2024.
[18] Sudeep Dasari, Mohan Kumar Srirama, Unnat Jain, and [29] Hao-Shu Fang, Chenxi Wang, Hongjie Fang, Minghao
Abhinav Gupta. An unbiased look at datasets for visuo- Gou, Jirong Liu, Hengxu Yan, Wenhai Liu, Yichen
motor pre-training. In Conference on Robot Learning, Xie, and Cewu Lu. Anygrasp: Robust and efficient
pages 1183–1198. PMLR, 2023. grasp perception in spatial and temporal domains. IEEE
[19] Matt Deitke, Christopher Clark, Sangho Lee, Rohun Transactions on Robotics, 39(5):3929–3945, 2023.
Tripathi, Yue Yang, Jae Sung Park, Mohammadreza [30] Hao-Shu Fang, Hongjie Fang, Zhenyu Tang, Jirong Liu,
Salehi, Niklas Muennighoff, Kyle Lo, Luca Soldaini, Chenxi Wang, Junbo Wang, Haoyi Zhu, and Cewu Lu.
et al. Molmo and pixmo: Open weights and open data Rh20t: A comprehensive robotic dataset for learning
for state-of-the-art multimodal models. arXiv preprint diverse skills in one-shot. In 2024 IEEE International
arXiv:2409.17146, 2024. Conference on Robotics and Automation (ICRA), pages
[20] Dempsey. Reviews-consumer technology. the teardown- 653–660. IEEE, 2024.
amazon astro consumer robot. Engineering & Technol- [31] Theophile Gervet, Soumith Chintala, Dhruv Batra, Ji-
ogy, 18(2):70–71, 2023. tendra Malik, and Devendra Singh Chaplot. Navigating
[21] Jacob Devlin, Ming-Wei Chang, Kenton Lee, and to objects in the real world. Science Robotics, 8(79):
Kristina Toutanova. Bert: Pre-training of deep bidirec- eadf6991, 2023.
tional transformers for language understanding. In Pro- [32] Yash Goyal, Tejas Khot, Douglas Summers-Stay, Dhruv
ceedings of the 2019 Conference of the North American Batra, and Devi Parikh. Making the V in VQA matter:
Chapter of the Association for Computational Linguis- Elevating the role of image understanding in visual
tics: Human Language Technologies, 2019. question answering. In Computer Vision and Pattern
[22] Ria Doshi, Homer Walke, Oier Mees, Sudeep Dasari, Recognition (CVPR), 2017.
and Sergey Levine. Scaling cross-embodied learning: [33] Abhinav Gupta, Adithyavairavan Murali,
Onepolicyformanipulation,navigation,locomotionand Dhiraj Prakashchand Gandhi, and Lerrel Pinto.
aviation. In Conference on Robot Learning, 2024. Robot learning in homes: Improving generalization and
[23] DannyDriess,FeiXia,MehdiSMSajjadi,CoreyLynch, reducing dataset bias. Advances in neural information
Aakanksha Chowdhery, Brian Ichter, Ayzaan Wahid, processing systems, 31, 2018.
JonathanTompson,QuanVuong,TianheYu,etal. Palm- [34] Kaiming He, Xiangyu Zhang, Shaoqing Ren, and Jian
e: An embodied multimodal language model. arXiv Sun. Deep residual learning for image recognition. In
preprint arXiv:2303.03378, 2023. Proceedings of the IEEE conference on computer vision
[24] Jiafei Duan, Wentao Yuan, Wilbert Pumacay, Yi Ru and pattern recognition, pages 770–778, 2016.
Wang, Kiana Ehsani, Dieter Fox, and Ranjay Kr- [35] KaimingHe,XinleiChen,SainingXie,YanghaoLi,Piotr
ishna. Manipulate-anything: Automating real-world Dolla´r, and Ross Girshick. Masked autoencoders are
robots using vision-language models. arXiv preprint scalablevisionlearners. InProceedingsoftheIEEE/CVF
arXiv:2406.18915, 2024. ConferenceonComputerVisionandPatternRecognition,
[25] Frederik Ebert, Yanlai Yang, Karl Schmeckpeper, pages 15979–15988, 2022.
Bernadette Bucher, Georgios Georgakis, Kostas Dani- [36] Yingdong Hu, Fanqi Lin, Tong Zhang, Li Yi, and Yang
ilidis, Chelsea Finn, and Sergey Levine. Bridge data: Gao. Look before you leap: Unveiling the power of gpt-

--- Page 14 ---
4v in robotic vision-language planning. arXiv preprint [43] Alexander Kirillov, Eric Mintun, Nikhila Ravi, Hanzi
arXiv:2311.17842, 2023. Mao, Chloe Rolland, Laura Gustafson, Tete Xiao,
[37] Huang Huang, Fangchen Liu, Letian Fu, Tingfan Wu, Spencer Whitehead, Alexander C. Berg, Wan-Yen Lo,
Mustafa Mukadam, Jitendra Malik, Ken Goldberg, and PiotrDolla´r,andRossGirshick.Segmentanything.arXiv
Pieter Abbeel. Otter: A vision-language-action model preprint arXiv:2304.02643, 2023.
with text-aware visual feature extraction. arXiv preprint [44] Boyi Li, Philipp Wu, Pieter Abbeel, and Jitendra Malik.
arXiv:2503.03734, 2025. Interactive task planning with language models, 2023.
[38] Wenlong Huang, Pieter Abbeel, Deepak Pathak, and [45] Qixiu Li, Yaobo Liang, Zeyu Wang, Lin Luo, Xi Chen,
Igor Mordatch. Language models as zero-shot planners: Mozheng Liao, Fangyun Wei, Yu Deng, Sicheng Xu,
Extracting actionable knowledge for embodied agents. Yizhong Zhang, et al. Cogact: A foundational
In International conference on machine learning, pages vision-language-action model for synergizing cognition
9118–9147. PMLR, 2022. and action in robotic manipulation. arXiv preprint
[39] Aaron Jaech, Adam Kalai, Adam Lerer, Adam Richard- arXiv:2411.19650, 2024.
son, Ahmed El-Kishky, Aiden Low, Alec Helyar, Alek- [46] Xiang Li, Cristina Mata, Jongwoo Park, Kumara Ka-
sander Madry, Alex Beutel, Alex Carney, et al. Openai hatapitiya, Yoo Sung Jang, Jinghuan Shang, Kanchana
o1 system card. arXiv preprint arXiv:2412.16720, 2024. Ranasinghe, Ryan Burgert, Mu Cai, Yong Jae Lee, et al.
[40] Joseph L Jones. Robots at the tipping point: the road to Llara: Supercharging robot learning data for vision-
irobot roomba. IEEE Robotics & Automation Magazine, languagepolicy. arXivpreprintarXiv:2406.20095,2024.
13(1):76–78, 2006. [47] Yi Li, Yuquan Deng, Jesse Zhang, Joel Jang, Marius
[41] Alexander Khazatsky, Karl Pertsch, Suraj Nair, Ash- Memmel, Raymond Yu, Caelan Reed Garrett, Fabio
win Balakrishna, Sudeep Dasari, Siddharth Karam- Ramos,DieterFox,AnqiLi,etal. Hamster:Hierarchical
cheti, Soroush Nasiriany, Mohan Kumar Srirama, action models for open-world robot manipulation. arXiv
Lawrence Yunliang Chen, Kirsty Ellis, Peter David preprint arXiv:2502.05485, 2025.
Fagan, Joey Hejna, Masha Itkina, Marion Lepert, [48] Jacky Liang, Wenlong Huang, Fei Xia, Peng Xu, Karol
Yecheng Jason Ma, Patrick Tree Miller, Jimmy Wu, Hausman, Brian Ichter, Pete Florence, and Andy Zeng.
SuneelBelkhale,ShivinDass,HuyHa,ArhanJain,Abra- Code as policies: Language model programs for em-
ham Lee, Youngwoon Lee, Marius Memmel, Sungjae bodied control. In 2023 IEEE International Conference
Park, Ilija Radosavovic, Kaiyuan Wang, Albert Zhan, on Robotics and Automation (ICRA), pages 9493–9500.
Kevin Black, Cheng Chi, Kyle Beltran Hatch, Shan IEEE, 2023.
Lin, Jingpei Lu, Jean Mercat, Abdul Rehman, Pan- [49] Fanqi Lin, Yingdong Hu, Pingyue Sheng, Chuan Wen,
nag R Sanketi, Archit Sharma, Cody Simpson, Quan Jiacheng You, and Yang Gao. Data scaling laws in im-
Vuong, Homer Rich Walke, Blake Wulfe, Ted Xiao, itation learning for robotic manipulation. arXiv preprint
Jonathan Heewon Yang, Arefeh Yavary, Tony Z. Zhao, arXiv:2410.18647, 2024.
Christopher Agia, Rohan Baijal, Mateo Guaman Cas- [50] YaronLipman,RickyTQChen,HeliBen-Hamu,Maxim-
tro, Daphne Chen, Qiuyu Chen, Trinity Chung, Jaimyn ilian Nickel, and Matt Le. Flow matching for generative
Drake, Ethan Paul Foster, Jensen Gao, David Antonio modeling. arXiv preprint arXiv:2210.02747, 2022.
Herrera, Minho Heo, Kyle Hsu, Jiaheng Hu, Donovon [51] Fangchen Liu, Kuan Fang, Pieter Abbeel, and Sergey
Jackson, Charlotte Le, Yunshuang Li, Kevin Lin, Roy Levine. Moka: Open-vocabulary robotic manipulation
Lin,ZehanMa,AbhiramMaddukuri,SuvirMirchandani, throughmark-basedvisualprompting. InFirstWorkshop
Daniel Morton, Tony Nguyen, Abigail O’Neill, Rosario on Vision-Language Models for Navigation and Manip-
Scalise, Derick Seale, Victor Son, Stephen Tian, Emi ulation at ICRA 2024, 2024.
Tran, Andrew E. Wang, Yilin Wu, Annie Xie, Jingyun [52] JiamingLiu,HaoChen,PengjuAn,ZhuoyangLiu,Ren-
Yang, Patrick Yin, Yunchu Zhang, Osbert Bastani, Glen rui Zhang, Chenyang Gu, Xiaoqi Li, Ziyu Guo, Sixiang
Berseth, Jeannette Bohg, Ken Goldberg, Abhinav Gupta, Chen, Mengzhen Liu, et al. Hybridvla: Collaborative
Abhishek Gupta, Dinesh Jayaraman, Joseph J Lim, Ji- diffusionandautoregressioninaunifiedvision-language-
tendra Malik, Roberto Mart´ın-Mart´ın, Subramanian Ra- action model. arXiv preprint arXiv:2503.10631, 2025.
mamoorthy, Dorsa Sadigh, Shuran Song, Jiajun Wu, [53] Peiqi Liu, Yaswanth Orru, Jay Vakil, Chris Paxton, Nur
Michael C. Yip, Yuke Zhu, Thomas Kollar, Sergey Muhammad Mahi Shafiullah, and Lerrel Pinto. Ok-
Levine, and Chelsea Finn. Droid: A large-scale in- robot:Whatreallymattersinintegratingopen-knowledge
the-wild robot manipulation dataset. In Proceedings of models for robotics. arXiv preprint arXiv:2401.12202,
Robotics: Science and Systems, 2024. 2024.
[42] Moo Jin Kim, Karl Pertsch, Siddharth Karamcheti, Ted [54] Qiang Liu. Rectified flow: A marginal preserv-
Xiao, Ashwin Balakrishna, Suraj Nair, Rafael Rafailov, ing approach to optimal transport. arXiv preprint
EthanFoster,GraceLam,PannagSanketi,etal.Openvla: arXiv:2209.14577, 2022.
An open-source vision-language-action model. arXiv [55] SongmingLiu,LingxuanWu,BangguoLi,HengkaiTan,
preprint arXiv:2406.09246, 2024. Huayu Chen, Zhengyi Wang, Ke Xu, Hang Su, and Jun

--- Page 15 ---
Zhu. Rdt-1b: a diffusion foundation model for bimanual hyek Han, Kanishka Rao, Karl Pertsch, Karol Hausman,
manipulation. arXiv preprint arXiv:2410.07864, 2024. Keegan Go, Keerthana Gopalakrishnan, Ken Goldberg,
[56] Jeffrey Mahler, Jacky Liang, Sherdil Niyaz, Michael Kendra Byrne, Kenneth Oslund, Kento Kawaharazuka,
Laskey, Richard Doan, Xinyu Liu, Juan Aparicio Ojea, Kevin Zhang, Keyvan Majd, Krishan Rana, Krishnan
and Ken Goldberg. Dex-net 2.0: Deep learning to plan Srinivasan,LawrenceYunliangChen,LerrelPinto,Liam
robust grasps with synthetic point clouds and analytic Tan, Lionel Ott, Lisa Lee, Masayoshi Tomizuka, Max-
grasp metrics. arXiv preprint arXiv:1703.09312, 2017. imilian Du, Michael Ahn, Mingtong Zhang, Mingyu
[57] Arjun Majumdar, Karmesh Yadav, Sergio Arnaud, Jason Ding, Mohan Kumar Srirama, Mohit Sharma, Moo Jin
Ma, Claire Chen, Sneha Silwal, Aryan Jain, Vincent- Kim,NaoakiKanazawa,NicklasHansen,NicolasHeess,
PierreBerges,TingfanWu,JayVakil,etal.Wherearewe Nikhil J Joshi, Niko Suenderhauf, Norman Di Palo,
in the search for an artificial visual cortex for embodied Nur Muhammad Mahi Shafiullah, Oier Mees, Oliver
intelligence? AdvancesinNeuralInformationProcessing Kroemer, Pannag R Sanketi, Paul Wohlhart, Peng Xu,
Systems, 36:655–677, 2023. Pierre Sermanet, Priya Sundaresan, Quan Vuong, Rafael
[58] Suraj Nair, Aravind Rajeswaran, Vikash Kumar, Chelsea Rafailov, Ran Tian, Ria Doshi, Roberto Mart´ın-Mart´ın,
Finn, and Abhinav Gupta. R3m: A universal visual Russell Mendonca, Rutav Shah, Ryan Hoque, Ryan Ju-
representation for robot manipulation. In CoRL, 2022. lian, Samuel Bustamante, Sean Kirmani, Sergey Levine,
[59] SoroushNasiriany,FeiXia,WenhaoYu,TedXiao,Jacky Sherry Moore, Shikhar Bahl, Shivin Dass, Shuran Song,
Liang,IshitaDasgupta,AnnieXie,DannyDriess,Ayzaan Sichun Xu, Siddhant Haldar, Simeon Adebola, Simon
Wahid, Zhuo Xu, et al. Pivot: Iterative visual prompting Guist, Soroush Nasiriany, Stefan Schaal, Stefan Welker,
elicits actionable knowledge for vlms. arXiv preprint StephenTian,SudeepDasari,SuneelBelkhale,Takayuki
arXiv:2402.07872, 2024. Osa, Tatsuya Harada, Tatsuya Matsushima, Ted Xiao,
[60] Hai Nguyen and Charles C Kemp. Autonomously learn- Tianhe Yu, Tianli Ding, Todor Davchev, Tony Z. Zhao,
ing to visually detect where manipulation will succeed. Travis Armstrong, Trevor Darrell, Vidhi Jain, Vincent
Autonomous Robots, 36:137–152, 2014. Vanhoucke, Wei Zhan, Wenxuan Zhou, Wolfram Bur-
[61] Dantong Niu, Yuvan Sharma, Giscard Biamby, Jerome gard, Xi Chen, Xiaolong Wang, Xinghao Zhu, Xuanlin
Quenum, Yutong Bai, Baifeng Shi, Trevor Darrell, and Li, Yao Lu, Yevgen Chebotar, Yifan Zhou, Yifeng Zhu,
RoeiHerzig. Llarva:Vision-actioninstructiontuningen- Ying Xu, Yixuan Wang, Yonatan Bisk, Yoonyoung Cho,
hances robot learning. arXiv preprint arXiv:2406.11815, YoungwoonLee,YuchenCui,YuehhuaWu,YujinTang,
2024. Yuke Zhu, Yunzhu Li, Yusuke Iwasawa, Yutaka Matsuo,
[62] Octo Model Team, Dibya Ghosh, Homer Walke, Karl Zhuo Xu, and Zichen Jeff Cui. Open X-Embodiment:
Pertsch, Kevin Black, Oier Mees, Sudeep Dasari, Joey Robotic learning datasets and RT-X models. https:
Hejna, Charles Xu, Jianlan Luo, Tobias Kreiman, You //arxiv.org/abs/2310.08864, 2023.
Liang Tan, Pannag Sanketi, Quan Vuong, Ted Xiao, [64] Karl Pertsch, Kyle Stachowicz, Brian Ichter, Danny
Dorsa Sadigh, Chelsea Finn, and Sergey Levine. Octo: Driess, Suraj Nair, Quan Vuong, Oier Mees, Chelsea
Anopen-sourcegeneralistrobotpolicy.InProceedingsof Finn, and Sergey Levine. FAST: Efficient action tok-
Robotics:ScienceandSystems,Delft,Netherlands,2024. enization for vision-language-action models. Robotics:
[63] Open X-Embodiment Collaboration, Abhishek Padalkar, Science and Systems, 2025.
Acorn Pooley, Ajinkya Jain, Alex Bewley, Alex Her- [65] Dicong Qiu, Wenzong Ma, Zhenfu Pan, Hui Xiong, and
zog, Alex Irpan, Alexander Khazatsky, Anant Rai, Junwei Liang. Open-vocabulary mobile manipulation in
AnikaitSingh,AnthonyBrohan,AntoninRaffin,Ayzaan unseen dynamic environments with 3d semantic maps.
Wahid, Ben Burgess-Limerick, Beomjoon Kim, Bern- arXiv preprint arXiv:2406.18115, 2024.
hard Scho¨lkopf, Brian Ichter, Cewu Lu, Charles Xu, [66] Alec Radford, Jong Wook Kim, Chris Hallacy, Aditya
Chelsea Finn, Chenfeng Xu, Cheng Chi, Chenguang Ramesh, Gabriel Goh, Sandhini Agarwal, Girish Sastry,
Huang, Christine Chan, Chuer Pan, Chuyuan Fu, Coline Amanda Askell, Pamela Mishkin, Jack Clark, et al.
Devin, Danny Driess, Deepak Pathak, Dhruv Shah, Di- Learning transferable visual models from natural lan-
eterBu¨chler,DmitryKalashnikov,DorsaSadigh,Edward guage supervision. In International conference on ma-
Johns, Federico Ceola, Fei Xia, Freek Stulp, Gaoyue chine learning, pages 8748–8763. PMLR, 2021.
Zhou, Gaurav S. Sukhatme, Gautam Salhotra, Ge Yan, [67] Nur Muhammad Mahi Shafiullah, Anant Rai, Haritheja
Giulio Schiavi, Hao Su, Hao-Shu Fang, Haochen Shi, Etukuru,YiqianLiu,IshanMisra,SoumithChintala,and
Heni Ben Amor, Henrik I Christensen, Hiroki Furuta, Lerrel Pinto. On bringing robots home. arXiv preprint
Homer Walke, Hongjie Fang, Igor Mordatch, Ilija Ra- arXiv:2311.16098, 2023.
dosavovic, Isabel Leal, Jacky Liang, Jaehyung Kim, [68] Dhruv Shah, Ajay Sridhar, Arjun Bhorkar, Noriaki Hi-
Jan Schneider, Jasmine Hsu, Jeannette Bohg, Jeffrey rose, and Sergey Levine. Gnm: A general navigation
Bingham, Jiajun Wu, Jialin Wu, Jianlan Luo, Jiayuan model to drive any robot. In 2023 IEEE International
Gu, Jie Tan, Jihoon Oh, Jitendra Malik, Jonathan Tomp- Conference on Robotics and Automation (ICRA), pages
son, Jonathan Yang, Joseph J. Lim, Joa˜o Silve´rio, Jun- 7226–7233. IEEE, 2023.

--- Page 16 ---
[69] Dhruv Shah, Ajay Sridhar, Nitish Dashora, Kyle Sta- and Illia Polosukhin. Attention is all you need. In
chowicz, Kevin Black, Noriaki Hirose, and Sergey Advances in Neural Information Processing Systems,
Levine. ViNT:Afoundationmodelforvisualnavigation. volume 30, 2017.
In7thAnnualConferenceonRobotLearning,2023.URL [80] Homer Rich Walke, Kevin Black, Tony Z Zhao, Quan
https://arxiv.org/abs/2306.14846. Vuong, Chongyi Zheng, Philippe Hansen-Estruch, An-
[70] Rutav Shah, Albert Yu, Yifeng Zhu, Yuke Zhu, and dre Wang He, Vivek Myers, Moo Jin Kim, Max Du,
RobertoMart´ın-Mart´ın. Bumble:Unifyingreasoningand et al. BridgeData v2: A dataset for robot learning at
acting with vision-language models for building-wide scale. In Conference on Robot Learning, pages 1723–
mobile manipulation. arXiv preprint arXiv:2410.06237, 1736. PMLR, 2023.
2024. [81] Shu Wang, Muzhi Han, Ziyuan Jiao, Zeyu Zhang,
[71] Lucy Xiaoyang Shi, Zheyuan Hu, Tony Z Zhao, Ar- Ying Nian Wu, Song-Chun Zhu, and Hangxin Liu. Llmˆ
chit Sharma, Karl Pertsch, Jianlan Luo, Sergey Levine, 3:Largelanguagemodel-basedtaskandmotionplanning
and Chelsea Finn. Yell at your robot: Improving with motion failure reasoning. In 2024 IEEE/RSJ Inter-
on-the-fly from language corrections. arXiv preprint national Conference on Intelligent Robots and Systems
arXiv:2403.12910, 2024. (IROS), pages 12086–12092. IEEE, 2024.
[72] Lucy Xiaoyang Shi, Brian Ichter, Michael Equi, Liy- [82] Jason Wei, Xuezhi Wang, Dale Schuurmans, Maarten
iming Ke, Karl Pertsch, Quan Vuong, James Tanner, Bosma, Fei Xia, Ed Chi, Quoc V Le, Denny Zhou,
Anna Walling, Haohuan Wang, Niccolo Fusai, et al. et al. Chain-of-thought prompting elicits reasoning in
Hi robot: Open-ended instruction following with hier- large language models. Advances in neural information
archical vision-language-action models. arXiv preprint processing systems, 35:24824–24837, 2022.
arXiv:2502.19417, 2025. [83] Junjie Wen, Yichen Zhu, Jinming Li, Minjie Zhu, Kun
[73] Ishika Singh, Valts Blukis, Arsalan Mousavian, Ankit Wu, Zhiyuan Xu, Ning Liu, Ran Cheng, Chaomin
Goyal, Danfei Xu, Jonathan Tremblay, Dieter Fox, Jesse Shen, Yaxin Peng, Feifei Feng, and Jian Tang.
Thomason, and Animesh Garg. Progprompt: Generating Tinyvla: Towards fast, data-efficient vision-language-
situated robot task plans using large language models. action models for robotic manipulation. arXiv preprint
In 2023 IEEE International Conference on Robotics and arXiv:2409.12514, 2024.
Automation (ICRA), pages 11523–11530. IEEE, 2023. [84] Junjie Wen, Yichen Zhu, Jinming Li, Zhibin Tang,
[74] AustinStone,TedXiao,YaoLu,KeerthanaGopalakrish- Chaomin Shen, and Feifei Feng. Dexvla: Vision-
nan, Kuang-Huei Lee, Quan Vuong, Paul Wohlhart, Bri- languagemodelwithplug-indiffusionexpertforgeneral
annaZitkovich,FeiXia,ChelseaFinn,etal. Open-world robot control. arXiv preprint arXiv:2502.05855, 2025.
object manipulation using pre-trained vision-language [85] TeteXiao,IlijaRadosavovic,TrevorDarrell,andJitendra
models. arXiv preprint arXiv:2303.00905, 2023. Malik. Masked visual pre-training for motor control.
[75] Andrew Szot, Bogdan Mazoure, Omar Attia, Aleksei arXiv preprint arXiv:2203.06173, 2022.
Timofeev,HarshAgrawal,DevonHjelm,ZheGan,Zsolt [86] Jianwei Yang, Reuben Tan, Qianhui Wu, Ruijie Zheng,
Kira, and Alexander Toshev. From multimodal llms to Baolin Peng, Yongyuan Liang, Yu Gu, Mu Cai,
generalist embodied agents: Methods and lessons. arXiv Seonghyeon Ye, Joel Jang, et al. Magma: A founda-
preprint arXiv:2412.08442, 2024. tion model for multimodal ai agents. arXiv preprint
[76] Gemini Robotics Team, Saminda Abeyruwan, Joshua arXiv:2502.13130, 2025.
Ainslie, Jean-Baptiste Alayrac, Montserrat Gonzalez [87] Qiying Yu, Quan Sun, Xiaosong Zhang, Yufeng Cui,
Arenas, Travis Armstrong, Ashwin Balakrishna, Robert Fan Zhang, Yue Cao, Xinlong Wang, and Jingjing Liu.
Baruch, Maria Bauza, Michiel Blokzijl, et al. Gemini Capsfusion: Rethinking image-text data at scale. In
robotics: Bringing ai into the physical world. arXiv Proceedings of the IEEE/CVF Conference on Computer
preprint arXiv:2503.20020, 2025. Vision and Pattern Recognition, pages 14022–14032,
[77] Peter Tong, Ellis Brown, Penghao Wu, Sanghyun Woo, 2024.
Adithya Jairam Vedagiri IYER, Sai Charitha Akula, [88] Michał Zawalski, William Chen, Karl Pertsch, Oier
Shusheng Yang, Jihan Yang, Manoj Middepogu, Ziteng Mees,ChelseaFinn,andSergeyLevine. Roboticcontrol
Wang, et al. Cambrian-1: A fully open, vision-centric via embodied chain-of-thought reasoning. In Conference
exploration of multimodal llms. Advances in Neural on Robot Learning, 2024.
InformationProcessingSystems,37:87310–87356,2024. [89] Qingqing Zhao, Yao Lu, Moo Jin Kim, Zipeng Fu,
[78] Hugo Touvron, Thibaut Lavril, Gautier Izacard, Xavier ZhuoyangZhang,YechengWu,ZhaoshuoLi,QianliMa,
Martinet, Marie-Anne Lachaux, Timothe´e Lacroix, Bap- Song Han, Chelsea Finn, et al. Cot-vla: Visual chain-
tiste Rozie`re, Naman Goyal, Eric Hambro, Faisal Azhar, of-thought reasoning for vision-language-action models.
et al. Llama: Open and efficient foundation language ComputerVisionandPatternRecognition(CVPR),2025.
models. arXiv preprint arXiv:2302.13971, 2023. [90] HaoyuZhen,XiaowenQiu,PeihaoChen,JinchengYang,
[79] Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Xin Yan, Yilun Du, Yining Hong, and Chuang Gan. 3d-
Uszkoreit,LlionJones,AidanNGomez,ŁukaszKaiser, vla: 3d vision-language-action generative world model.

--- Page 17 ---
arXiv preprint arXiv:2403.09631, 2024. all tasks in four different locations, that are consistent for all
[91] PeiyuanZhi,ZhiyuanZhang,YuZhao,MuzhiHan,Zeyu policies in a comparison, leading to a total of 40 evaluations
Zhang,ZhitianLi,ZiyuanJiao,BaoxiongJia,andSiyuan per policy for our standard evaluations. Evaluations were
Huang. Closed-loop open-vocabulary mobile manipula- carried out by interleaving execution of policies to control for
tionwithgpt-4v. arXivpreprintarXiv:2404.10220,2024. environmental changes. Some evaluations include cancelled
[92] Brianna Zitkovich, Tianhe Yu, Sichun Xu, Peng Xu, episodesduetorobotfailures,timelimitationsorothercauses,
Ted Xiao, Fei Xia, Jialin Wu, Paul Wohlhart, Stefan which are removed. In all cases we control the sample size to
Welker, Ayzaan Wahid, et al. Rt-2: Vision-language- be close and report statistical significance according to a two-
actionmodelstransferwebknowledgetoroboticcontrol. sidedt-testassumingvariablenumberoftrialswithintheplots.
In Conference on Robot Learning, pages 2165–2183. Thelanguagefollowingevaluationsfollowadifferentprotocol
PMLR, 2023. as described in the main text.
The evaluation metrics for the kitchen cleanup tasks, which
APPENDIX
includeplacingdishesintoasinkandstoringitemsinadrawer,
A. Contributions are detailed below.
Data collection and operations. Noah Brown, Michael Equi, • DishesinSink:Thetaskbeginswith4dishes(e.g.,plates,
Chelsea Finn, Lachy Groom, Suraj Nair, Lucy Xiaoyang Shi, bowls, cutting boards, utensils) placed near a sink. The
Anna Walling. robot’s goal is to place all of them in the sink.
Annotation and supplemental data. Danny Driess, Chelsea +1 For each item picked up.
Finn,NiccoloFusai,LachyGroom,BrianIchter,KarlPertsch, +1 For each item placed in the sink.
Allen Z. Ren, Laura Smith, Kyle Stachowicz, Quan Vuong, Maximum score: 8 points.
Anna Walling, Lili Yu. • Items in Drawer: The task begins with an item on a
Policy training and research. Kevin Black, Danny Driess, countertop. The robot must place the item into a drawer
Michael Equi, Chelsea Finn, Niccolo Fusai, Dibya Ghosh, beneath the counter.
Brian Ichter, Liyiming Ke, Sergey Levine, Suraj Nair, Karl
+1 Picking up the object.
Pertsch, Allen Z. Ren, Lucy Xiaoyang Shi, Laura Smith, Jost
+1 Opening the drawer.
Tobias Springenberg, Kyle Stachowicz, Quan Vuong, Homer
+1 Putting the object into the drawer.
Walke, Lili Yu.
+1 Closing the drawer (if the object is inside).
Policy infrastructure. Kevin Black, Karan Dhabalia, Danny
Maximum score: 4 points.
Driess, Manuel Y. Galliker, Dibya Ghosh, Adrian Li-Bell,
Next, we outline the evaluation metrics for the bedroom
Quan Vuong, Haohuan Wang, Ury Zhilinsky.
cleanup tasks: putting laundry away and making a bed.
Robot hardware. Noah Brown, Adnan Esmail, Tim Jones,
Devin LeBlanc, Mohith Mothukuri. • Laundry in Basket: The task begins with an article of
clothing lying on the ground. The robot’s goal is to pick
Robot infrastructure. James Darpinian, Adnan Esmail,
up the laundry and place it in the laundry basket.
Manuel Y. Galliker, Karol Hausman, Szymon Jakubczak,
+1 Navigating to and picking up the clothing.
James Tanner.
+1 Placing the clothing into or on the laundry basket.
Writingandillustration.KevinBlack,DannyDriess,Chelsea
+1 Clothing is fully inside the basket.
Finn, Karol Hausman, Brian Ichter, Sergey Levine, Karl
Pertsch, Allen Z. Ren, Lucy Xiaoyang Shi, Jost Tobias Sprin- Maximum score: 3 points.
genberg. • Make the Bed: The bed starts unmade. The robot must
tidy the blanket and place two pillows at the head of the
B. Task evaluation rubric
bed.
For a quantitative evaluation of our method we performed +1 Straightening the blanket so it covers the sheets.
rigorous evaluation of a subset of four tasks that are included +1 Placing one pillow at the head of the bed.
in the training dataset (but evaluated in entirely new scenes +1 Placing the second pillow at the head of the bed.
and configurations). Among these are two kitchen cleanup +1 Blanket is straightened very neatly.
tasks and two bedroom cleanup tasks. Each task is evaluated +1 Both pillows are placed very neatly.
with a consistent set of items for each of the policies within
Maximum score: 5 points.
a comparison (but items varied between locations) in three
C. Language following experiment setup
different homes and three different mock kitchens and mock
bedrooms respectively (a total of 12 different locations). For Thelanguagefollowingexperimentsusetwounseenkitchen
each evaluation and each policy, unless otherwise stated, we scenes to test how well the model follows more specific
perform 10 evaluations per task; note that each of these user commands, such as “put the scissors in the drawer” or
evaluation episodes can span multiple minutes and they are “put the cutting board into the sink”. Each trial requires the
thus time intensive. We present results as percent of total robot to interpret the instruction, identify the correct object
points achieved in each evaluation rubric (as outlined below) amidst distractors, and perform the task. We evaluate on two
and present either per task metrics or metrics averaged across scenarios:

--- Page 18 ---
1) Items in the drawer: common kitchen items (tongs,
wooden serving spoon, can opener, scissors, and small
yellow mustard).
2) Items in the sink: common dining items (cup, bowl,
plate, plastic spoon, and cutting board).
In each trial, the robot is presented with five objects and
is instructed to move one of them. To discourage shortcut
behaviors, the target object is placed further away than the
distractors, such that a policy that is unable to interpret
the command should achieve only ∼20% language following
accuracy.Wereporttwometrics,averagedoverbothscenarios: Fig. 16: Per-task performance breakdown for training recipe ablations.
language following rate,whichmeasureswhetherthecorrect We evaluate each training mixture variant on four representative household
tasks: Items in Drawer, Dishes in Sink, Laundry Basket, and Make Bed.
object was selected, and task success rate, which evaluates
Removingcross-embodimentdata(MEorCE)leadstosignificantdegradation
whether the object was successfully placed in the specified inspecifictasks,particularlyItemsinDrawerandDishesinSink.Webdata
location. We further investigate how the number of distinct (WD) shows greater effect on the task (Items in Drawer) where the broad
knowledgeofthesceneisdesired.
training environments influences the model’s ability to gener-
alize to previously unseen objects. We design a similar Items
inthedrawertaskwithnovelhouseholditems(afunnel,apill
D. Per-task performance breakdown
bottle, a grill lighter, a lighter, and a pair of safety goggles).
a) Co-training recipe ablations: To better understand
None of these object categories were present in the training
the influence of different training data sources on specific
set, ensuring that this task tests the robot’s performance on
taskcategories,weprovideaper-taskperformancebreakdown
out-of-distribution objects. We show the example initial scene
(Figure 16). Here we consider four representative household
of each task in Figure 14.
tasks: Items in Drawer, Dishes in Sink, Laundry Basket,
Along with data ablation experiments in Figure 11 and
and Make Bed. In summary, the results indicate that cross-
location scaling experiments in Figure 9, Figure 15 presents
embodiment transfer and diverse data co-training are critical
language following results across model classes. We find
forgeneralizationacrossarangeoftasks,withvaryingdegrees
that π follows language at a slightly higher rate than π -
0.5 0 of reliance depending on task requirements.
FAST+Flow, and a much higher rate than π , indicating the
0 ForItemsinDrawer,performancedropssubstantiallywhen
importance of discrete token training on language following
cross-embodiment data (ME or CE) or web data (WD) is
abilities.
removed, with the largest degradation observed when all are
excluded. This task requires recognizing and understanding
a very broad class of common objects, and such knowledge
may be learned from diverse data sources. In contrast, Dishes
in Sink remains relatively robust to the removal of web data
(WD) but degrades when cross-embodiment data (ME or CE)
is excluded, anchoring the intuition that this task primarily
(a) In-distribution objects, (b) In-distribution objects, (c) Out-of-distribution ob- requires general manipulation strategies learned from robotic
itemsindrawer dishesinsink jects,itemsindrawer
data. Laundry Basket and Make Bed also exhibit performance
Fig.14:Exampleinitialstatesofdifferentlanguagefollowingexperiments. degradation when cross-embodiment data is removed, but are
generally less sensitive to other changes in the data mixture.
b) High-level model analysis: For a more granular view
of how different high-level inference methods affect specific
task categories, we again provide a per-task breakdown (Fig-
ure 17). We evaluate the full π model and all high-level
0.5
inference baselines across four representative tasks: Items in
Drawer, Dishes in Sink, Laundry Basket, and Make Bed.
The results show that explicit high-level inference improves
performance across tasks, with the full π model achieving
0.5
the best overall results.
For Items in Drawer and Dishes in Sink, high-level infer-
ence is critical: performance drops substantially with the no
Fig. 15: Comparing π0.5 with other models on language following. We HL variant, indicating the importance of structured subtask
evaluate language following capabilities of π0.5 , π0, and π0-FAST+Flow, prediction and long-horizon planning. In these two tasks, the
findingπ0.5 outperformseach,andπ0 byawidemargin.
π model also outperforms GPT-4 HL, showing the benefit
0.5
ofin-domainfine-tuninganddemonstratingthatthehigh-level

--- Page 19 ---
Fig.17:Per-task performance breakdown for high-level inference meth-
ods. We evaluate the full π0.5 model and various high-level inference
baselinesacrossfourrepresentativehouseholdtasks.
model learns strategies that help the low-level policy succeed.
In Items in Drawer, performance also declines sharply when
web data is removed — this echos the result from the co-
training recipe ablation and highlights the importance of
semantic knowledge for generalizing to less seen objects. For
Fig.18:Exampleoftheπ0.5 attentionmaskingpattern.
LaundryBasket andDishesinSink,themodelislesssensitive
to the choice of the high-level policy. These tasks are either
relatively shorter in horizon or require less detailed semantic Embeddings from the VLM and action expert interact
reasoning. only through self-attention. A full prefix mask is used on
images, prompt tokens, and proprioceptive state; FAST action
E. Model technical details
tokens attend to this prefix and auto-regressively on previous
The π model builds upon π and adopts the PaliGemma actiontokens.Embeddingsfromtheactionexpertembeddings
0.5 0
VLM [5] as the backbone for visual-language understanding attend to the prefix and to one another, but do not attend to
as well as an “action expert” for fast action generation. The FAST action tokens to avoid information leakage between the
VLM backbone takes in a sequence of images [I1,...,In] two representations of actions. In effect, information flows
t t
and a language prompt ℓ as in π , but also the robot’s unidirectionally from the VLM to the action expert; no VLM
0
proprioceptivestateq intokenizedformandtokenizedactions embedding attends to the action expert. An example of the
t
[64], which will be auto-regressively predicted. The action attention mask at each layer is visualized in Figure 18.
expert is a smaller transformer that takes in a sequence of We follow π for sampling the flow-matching timestep
0
noisy action tokens aτ,ω for an action horizon of 50, i.e. τ. In summary we deviate from standard uniform sampling
t:t+H
H = 49, and is trained with the flow matching objective. τ ∼ U(0,1) [50, 54] or methods emphasizing midrange
The noisy action chunk (with action dimension d) is first timesteps [27], and instead use a time-step sampling distri-
projected to the transformer embedding dimension using a bution that emphasizes low time-steps [8], given by p(τ) =
single linear layer. Unlike π that fuses the flow-matching Beta(s−τ;α = 1.5,β = 1). Timesteps above the threshold
0 s
timestep τ with the noisy action before being fed into the s are excluded from sampling, as they are not needed if the
transformer, π uses a separate MLP for projecting τ only integration step δ satisfies δ > 1−s. We use s = 0.999 in
0.5
and then applies adaptive RMSNorm to inject the timestep ourexperiments,whichaccommodatesupto1,000integration
information to each layer of the action expert. The timestep steps (δ >0.001).
MLPtakesintheformofswish(W ·swish(W ·ϕ(τ))),where Weapplyimageaugmentation(randomcrop,resizing,rota-
2 1
ϕ:R→Rw is a sinusoidal positional encoding function [79] tion,andcolorjittering)toallinputimagesusingthefollowing
andW ,W ∈Rw×w.Theactionexpertoutputsactiontokens hyper-parameters and in this order
1 2
ya ,whicharethendecodedintothetargetvectorfieldusing
1:H transforms = [
1
a final linear projection. 2 augmax.RandomCrop(int(width * 0.95), int(
Thedimensionsofthetwotransformersarethesameasπ 0 : height * 0.95)),
{width=2048, depth=18, mlp dim=16,384, num heads=18,3 augmax.Resize(width, height),
augmax.Rotate((-5, 5)),
num kv heads=1, head dim=256} for the 2B VLM initial-4
augmax.ColorJitter(brightness=0.3,
ized from PaliGemma weights, and the same except for5
contrast=0.4, saturation=0.5),
{width=1024,mlp dim=4096}fortheactionexpertwith300M ]
6
parameters.