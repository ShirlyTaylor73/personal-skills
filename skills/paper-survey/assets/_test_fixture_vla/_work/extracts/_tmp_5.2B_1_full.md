--- Page 1 ---
π : A Vision-Language-Action Flow Model for
0
General Robot Control
Physical Intelligence
Kevin Black, Noah Brown, Danny Driess, Adnan Esmail, Michael Equi, Chelsea Finn, Niccolo Fusai,
Lachy Groom, Karol Hausman, Brian Ichter, Szymon Jakubczak, Tim Jones, Liyiming Ke, Sergey Levine,
Adrian Li-Bell, Mohith Mothukuri, Suraj Nair, Karl Pertsch, Lucy Xiaoyang Shi, James Tanner, Quan Vuong,
Anna Walling, Haohuan Wang, Ury Zhilinsky
https://physicalintelligence.company/blog/pi0
Z)0./(cid:15)(cid:15)(cid:20)GSO/,(cid:25)SG(cid:23)L Ÿ(cid:23)(cid:13)G.(cid:23)G(cid:13)(cid:20)(cid:15)0(cid:18)%G) °2G(cid:23))©(cid:20)¯SO/,(cid:25)SG(cid:23)(cid:13))¡(cid:18)(cid:13)(cid:18)(cid:15)G(cid:13) (cid:8)(cid:5)(cid:7)(cid:6)(cid:4)(cid:1)(cid:3)(cid:6)(cid:2)(cid:0)(cid:25)(cid:23)(cid:20)(cid:19)(cid:24)(cid:16)(cid:14)(cid:21)(cid:24)(cid:12)(cid:11)(cid:14)(cid:24)(cid:17)(cid:22)(cid:10)(cid:13)(cid:18)(cid:15)(cid:9)(cid:15)
./O/(cid:13)),(cid:18)(cid:13)(cid:18)(cid:15)G(cid:13) 2.G(cid:20)(cid:13).(cid:18)(cid:25)(cid:23)(cid:25)(cid:23)(
O'(cid:15))(cid:13)(cid:18)O%G
O'(cid:15))(cid:13)(cid:18)O%G 2(cid:18)0(cid:9))O/(cid:13)(cid:13)%G(cid:15)
m # (cid:5)!(cid:31)(cid:30)(cid:29)(cid:31)(cid:28)(cid:5)(cid:26)(cid:0)2/(cid:15)(cid:13)(cid:20)(cid:13).(cid:18)(cid:25)(cid:23)(cid:25)(cid:23)()(cid:13)/)
lhg(cid:25)(cid:15)(cid:25)/(cid:23)(cid:20)%(cid:18)(cid:23)('(cid:18)(G(cid:20)(cid:18)0(cid:13)(cid:25)/(cid:23))S/,G%
,(cid:25)&&(cid:25)0'%(cid:13))(cid:13)(cid:18)(cid:15)(cid:9)(cid:15)
O(cid:18)()(./0G.(cid:25)G(cid:15) /2G(cid:23))2/20/.(cid:23) 2.G(cid:20)(cid:13).(cid:18)(cid:25)(cid:23)G,)|{z (cid:18)0(cid:13)(cid:25)/(cid:23))
GŠ2G.(cid:13)
GS2(cid:13)³)(cid:18)2(cid:18).(cid:13)SG(cid:23)(cid:13)),.³G.
%/(cid:18),),(cid:25)(cid:15)pG(cid:15) (cid:15)/.(cid:13))%G(/(cid:15) y&/%,)(cid:15)p(cid:25).(cid:13)n
O(cid:18)(cid:13)0p)&/%,)(cid:15)p(cid:25).(cid:13)(cid:15)
Õ(cid:25)(p(cid:20)Ó'(cid:18)%(cid:25)(cid:13)³)2/(cid:15)(cid:13)(cid:20)(cid:13).(cid:18)(cid:25)(cid:23)(cid:25)(cid:23)(),(cid:18)(cid:13)(cid:18)
S(cid:18)(cid:9)G)0/&&GG (cid:15)ÀGG2)(cid:13)(cid:18)O%G 8::(cid:31)!(cid:31)(cid:5)7(cid:2)(cid:0)2/(cid:15)(cid:13)(cid:20)(cid:13).(cid:18)(cid:25)(cid:23)(cid:25)(cid:23)()(cid:13)/)
'(cid:23)(cid:15)GG(cid:23))(cid:13)(cid:18)(cid:15)(cid:9)(cid:15)
GS2(cid:13)³),.³G. (cid:15)G(cid:13))(cid:13)(cid:18)O%G
p(cid:25)(p),GŠ(cid:13)G.(cid:25)(cid:13)³)(cid:13)(cid:18)(cid:15)(cid:9)(cid:15)
2'(cid:13))(cid:25)(cid:13)GS(cid:15))(cid:25)(cid:23)),.(cid:18)ÀG.
2(cid:18)0(cid:9))(cid:15)pG%& &%(cid:18)(cid:13)(cid:13)G(cid:23))O/Š
(cid:18)(cid:23),)S(cid:18)(cid:23)³)S/.G± '(cid:23)(cid:15)GG(cid:23))(cid:13)(cid:18)(cid:15)(cid:9)(cid:15)
.G2%(cid:18)0G)2(cid:18)2G.)(cid:13)/ÀG%
Fig. 1: Our generalist robot policy uses a pre-trained vision-language model (VLM) backbone, as well as a diverse cross-
embodimentdatasetwithavarietyofdexterousmanipulationtasks.Themodelisadaptedtorobotcontrolbyaddingaseparate
action expert that produces continuous actions via flow matching, enabling precise and fluent manipulation skills. The model
can then be used directly to perform tasks based on a prompt, or fine-tuned on high-quality data to enable complex multi-stage
tasks, such as folding multiple articles of laundry or assembling a box.
Abstract—Robotlearningholdstremendouspromisetounlock built on top of a pre-trained vision-language model (VLM)
thefullpotentialofflexible,general,anddexterousrobotsystems, to inherit Internet-scale semantic knowledge. We then discuss
as well as to address some of the deepest questions in artificial how this model can be trained on a large and diverse dataset
intelligence. However, bringing robot learning to the level of from multiple dexterous robot platforms, including single-arm
generality required for effective real-world systems faces major robots, dual-arm robots, and mobile manipulators. We evaluate
obstacles in terms of data, generalization, and robustness. In our model in terms of its ability to perform tasks via direct
this paper, we discuss how generalist robot policies (i.e., robot prompting,followlanguageinstructionsfrompeopleandfroma
foundationmodels)canaddressthesechallenges,andhowwecan high-level VLM policy, and its ability to acquire new skills via
design effective generalist robot policies for complex and highly fine-tuning. Our results cover a wide variety of tasks, such as
dexterous tasks. We propose a novel flow matching architecture laundry folding, table cleaning, and assembling boxes.
PhysicalIntelligence,SanFrancisco,California,USA.Correspondanceto:
research@physicalintelligence.company
6202
naJ
8
]GL.sc[
4v46142.0142:viXra

--- Page 2 ---
Fig. 2: π controls a mobile manipulator to fold laundry. Our model is pre-trained on diverse data from 7 distinct robot
0
configurations and 68 tasks, and can then either be prompted directly or fine-tuned to complex downstream tasks, as in the
case of this laundry folding policy, which fetches laundry from a dryer, packs it into a hamper, brings the hamper to a folding
table, and then folds each article of clothing.
I. INTRODUCTION solutions. For example, if the goal is to recognize birds in
photographs, it is likely more expedient to pre-train on many
A human being should be able to change a diaper, plan different image-language associations and then fine-tune or
an invasion, butcher a hog, conn a ship, design a
promptforthebirdrecognitiontask,thanitistotrainononly
building, write a sonnet, balance accounts, build a
birdrecognitiondata.Similarly,wemayfindthatforeffective
wall, set a bone, comfort the dying, take orders, give
orders, cooperate, act alone, solve equations, analyze a specialized robot systems, it is more effective to first pre-train
new problem, pitch manure, program a computer, cook on highly diverse robot data, and then fine-tune or prompt for
a tasty meal, fight efficiently, die gallantly. the desired task. This can resolve the data scarcity challenge,
Specialization is for insects.
becausemanymoresourcesofdataareavailabletoageneralist
Robert A. Heinlein, Time Enough for Love model — including data from other tasks, other robots, or
even non-robot sources — and it may resolve robustness and
Artificial intelligence systems come in all shapes and sizes, generalization challenges, because the diverse data exhibits
from highly specialized systems that solve complex prob- a greater coverage of observations and actions, providing a
lems inaccessible to the human mind, such as predicting variety of scenes, corrections, and recovery behaviors that
the conformation of a protein [21], to systems that can might not be present in more narrow specialized data. Thus,
produce lifelike high-resolution images or videos based on adopting a large-scale pre-training approach to robot learning
textual prompts [40]. However, the axis along which human has the potential to address many of the field’s challenges
intelligence most outpaces machine intelligence is versatility: and make practical learning-enabled robots a reality, while
the ability to solve diverse tasks situated in varied physical at the same time furthering our understanding of the deepest
environments, while responding intelligently to environmental problems in artificial intelligence.
constraints, language commands, and unexpected perturba-
However, developing such generalist robot policies — i.e.,
tions. Perhaps the most tangible progress toward this kind of
robot foundation models — involves a number of major
versatility in AI can be seen in large language- and vision-
challenges. First, any such research must be done at a very
language models [1, 48]: systems that are pre-trained on large
largescale,becausethefullbenefitsoflarge-scalepre-training
and very diverse corpora of images and text from the web,
areoftennotpresentatsmallerscales[54].Second,itrequires
and then fine-tuned (“aligned”) using more carefully curated
developing the right model architectures that can effectively
datasets meant to induce the desired pattern of behavior
makeuseofdiversedatasources,whileatthesametimebeing
and responsiveness. While such models have been shown
able to represent the intricate and subtle behaviors necessary
to exhibit broad instruction-following and problem-solving
to interact with complex physical scenes. Third, it requires
abilities[53,27],theyarenottrulysituatedinaphysicalworld
the right training recipe. This is perhaps the most important
the way that people are, and their understanding of physical
ingredient, as much of the recent progress with large models
interaction is based entirely on abstract descriptions. If such
in NLP and computer vision has relied heavily on delicate
methodsaretomaketangibleprogresstowardAIsystemsthat
strategies for curating pre-training and post-training data [35].
exhibit the kind of physically situated versatility that people
possess,wewillneedtotrainthemonphysicallysituateddata In this paper, we present a prototype model and learning
— that is, data from embodied robot agents. framework, which we call π , that illustrates how each of
0
Flexible and general-purpose models that can be tasked these three bottlenecks could be tackled. We illustrate our
to perform a variety of robot behaviors have tremendous model and system in Figure 1. To incorporate diverse data
practical ramifications, but they may also offer solutions to sources, we begin by utilizing a pre-trained vision-language
some of the toughest challenges facing robot learning today, model (VLM) to import Internet-scale experience. By basing
such as availability of data, generalization, and robustness. In our model on a VLM, we inherit the general knowledge,
naturallanguage[1]andcomputervision[39],general-purpose semanticreasoning,andproblem-solvingabilitiesoflanguage-
foundation models that are pre-trained on diverse multi-task and vision-language models. We then further train our model
data tend to outperform narrowly tailored and specialized to incorporate robot actions, turning it into a vision-language-

--- Page 3 ---
action(VLA)model[7].Inordertomakeitfeasibletoutilize that are fine-tuned for robot control [7, 24, 55]. Such models
a variety of diverse robot data sources, we employ cross- employ autoregressive discretization to represent actions in a
embodiment training [10], where data from many robot types manner analogous to text tokens. In contrast, our model em-
is combined into the same model. These different robot types ploysanoveldesignthatfine-tunesaVLMtoproduceactions
havedifferentconfigurationspacesandactionrepresentations, via flow matching [32, 28], a variant of diffusion [20, 46].
including single and dual-arm systems, as well as mobile This allows us to handle high-frequency action chunks [57]
manipulators. Additionally, in order to make it possible to (up to 50 Hz) and highly dexterous tasks, which we show
perform highly dexterous and intricate physical tasks, we use poseamajorchallengeforpriorautoregressiveVLAs[7].This
an action chunking architecture [57] with flow matching (a resembles a number of recent works on diffusion models for
variant of diffusion) to represent complex continuous action actiongeneration[9,60].Incontrasttotheseworks,ourmodel
distributions[28,32].Thisenablesourmodeltocontrolrobots usesapre-trainedVLMbackbone[5].Ourcontributionisalso
at frequencies of up to 50 Hz for dexterous tasks such as fundamentally integrative, focusing on a framework for robot
laundry folding (see Figure 1). To combine flow matching foundation models, including not only the model architecture
with VLMs, we use a novel action expert that augments the itself but also a pre-training recipe, pre-training and post-
standard VLM with flow-based outputs. training phases, and a range of real-world experiments.
As with language models, the architecture of our model is Outside of robot control, many models have been proposed
only part of our method. In order to flexibly and robustly that combine pre-trained language models with diffusion [40,
perform complex tasks, we need the right training recipe. 41, 14], including models that specifically hybridize diffusion
Our recipe mirrors the pre-training/post-training separation and autoregressive large language models [19, 29, 59]. Such
commonly seen in exascale language- and image-language models are typically concerned with image generation, but
models [1, 48], where the model is first pre-trained on a very our action generation model builds on a number of previously
large and diverse corpus, and then fine-tuned on more narrow proposed concepts. Like Zhou et al. [59], we train our model
andmorecarefullycurateddatatoinducethedesiredpatternof viaadiffusion-style(flowmatching)lossappliedonindividual
behavior — in our case, dexterity, efficiency, and robustness. sequence elements, in lieu of the standard cross-entropy loss
Intuitively, training only on high-quality data does not teach for decoder-only transformers. Like Liu et al. [29], we use
the model how to recover from mistakes, since mistakes are a separate set of weights for the tokens corresponding to
rarely seen in such data. Training on only lower-quality pre- diffusion.IncorporatingtheseconceptsintoaVLAmodel,we
training data does not teach the model to act efficiently and introduce what to our knowledge is the first flow matching
robustly. Combining both provides the desired behavior: the VLAthatproduceshigh-frequencyactionchunksfordexterous
model attempts insofar as possible to act in a manner similar control.
to the high-quality data, but still has a repertoire of recoveries Our work also builds on a rich history of prior works on
and corrections that it can deploy in the case of a mistake. large-scalerobotlearning.Earlyworkinthisareaoftenutilized
The contributions of our work consist of a novel generalist self-supervised or autonomous data collection [26, 22, 8],
robot policy architecture based on VLM pre-training and flow providing a tractable data source for simple tasks such as
matching, and an empirical investigation of pre-training/post- grasping [18, 37] or pushing [56], but without the complexity
trainingrecipesforsuchrobotfoundationmodels.Weevaluate ofmoredexterousbehaviors.Morerecently,anumberofhigh-
our model out of the box with language commands, with quality datasets have been collected for robot control that
fine-tuning to downstream tasks, and in combination with a enablebroadgeneralization[23,10,52,33,34,43,13,6],but
high-level semantic policy that outputs intermediate language typicallyforsimplertasksthatconsistofobjectrelocationand
commandstoperformcomplexandtemporallyextendedtasks. rudimentaryfurnituremanipulation(e.g.,draweropening)[31,
While our model and system make use of a variety of ideas 15]. More dexterous tasks have been studied at a smaller
presented in recent work, the combination of ingredients is scale, typically with 10s or 100s of training trajectories [57],
novel, and the empirical evaluation demonstrates a level of equivalent to 10 or less hours. Since one of our aims is to
dexterity and generality that goes significantly beyond pre- study complex and dexterous behaviors, we utilize a much
viously demonstrated robot foundation models. We evaluate larger dataset, with about 10,000 hours of demonstrations,
our approach by pre-training on over 10,000 hours of robot complemented by the open-source OXE dataset [10]. To our
data, and fine-tuning to a variety of dexterous tasks, including knowledge, this represents by far the largest robot learning
laundry folding (see Figure 2), clearing a table, putting dishes experimentintermsoftheamountofrobotdata.Atthisscale,
inamicrowave,stackingeggsintoacarton,assemblingabox, we show that a more sophisticated pre-training/post-training
and bagging groceries. recipe is highly effective — analogously to the recipes used
for large language models, a pre-training phase endows our
II. RELATEDWORK
model with a broad base of knowledge, which is then refined
Our work builds on recently proposed methods in large- in a post-training phase with higher-quality curated data to
scale robot learning, as well as multimodal language models. achieve the desired behavior.
Our work is most closely related to recently proposed vision- The complexity of the tasks we illustrate goes significantly
language action (VLA) models, which use pre-trained VLMs beyondpriorwork.Whilerecentworkhasillustratedanumber

--- Page 4 ---
! - ,+* ... - ,+/
´ ³(cid:10)(cid:4)(cid:5)(cid:4)&(cid:8)J „‚(cid:0)€(|
(cid:127)(cid:3)y(cid:4)(cid:1)~(cid:4)w
u(cid:4)(cid:1)(cid:3)(cid:12)~9(cid:4)(cid:5)((cid:7)&
(cid:12)(cid:12)(cid:7)(cid:7)(cid:8)(cid:8)(cid:6)(cid:6)(cid:5)(cid:5)(cid:7)(cid:7)(cid:4)(cid:4)(cid:3)(cid:3)(cid:1)(cid:1)(cid:8)(cid:8)(cid:10)(cid:10)(cid:0)(cid:0)(cid:2)(cid:2)(cid:11)(cid:11)(cid:9)(cid:9) (cid:4)(cid:4)LL(cid:5)(cid:5)(cid:3)(cid:3)(((cid:1)(cid:1)(cid:0)(cid:0)(cid:8)(cid:8)DD(cid:12)(cid:12)(cid:8)(cid:8)(cid:7)(cid:7)JJ
(cid:27)(cid:28)(cid:27)(cid:29)(cid:28)(cid:31)(cid:29)(cid:19)(cid:31)(cid:23)(cid:19)(cid:21)(cid:23)(cid:20)(cid:21)(cid:26)(cid:20)(cid:18)(cid:26)(cid:18)(cid:18)(cid:17)(cid:18)(cid:16)(cid:17)(cid:21)(cid:16)(cid:25)(cid:21)(cid:21)(cid:25)(cid:24)(cid:21)(cid:15)(cid:24)(cid:22)(cid:15)(cid:22)(cid:22)(cid:14)(cid:22)(cid:21)(cid:14)(cid:20)(cid:21)(cid:13)(cid:20)p(cid:13)b(cid:30)(cid:30)(cid:16)(cid:16) \XZUYTVSPXRQRWNX[OVPRRN[
„•(cid:0)€(|
u(‹(cid:3)9(cid:8)(cid:0)
Â(cid:1)(cid:5)(cid:8)(cid:7)(cid:1)(cid:8)(cid:5)(cid:0) ·¶µ u(cid:4)(cid:1)(cid:3)(cid:12)~9(cid:4)(cid:5)((cid:7)&
(cid:12)(cid:7)(cid:8)(cid:6)(cid:5)(cid:7)(cid:4)(cid:3)(cid:1)(cid:3)(cid:1)¸
(cid:2)(cid:2)(cid:3)(cid:3)@@ (cid:2)(cid:2)(cid:3)(cid:3)@@ (cid:2)(cid:2)(cid:3)(cid:3)@@ ><(9(cid:10)(cid:0)&6(cid:3)(cid:7)(cid:5)3
¬(cid:0)(cid:4)(cid:1)(cid:10)(cid:0)•(cid:0)€(|
$ "# (cid:1)((cid:3)&(cid:8) ¥(cid:3)(cid:1)›9(cid:8)(cid:0)(cid:157)(cid:7)y(cid:0)
u(cid:4)(cid:1)(cid:3)(cid:12)~9(cid:4)(cid:5)((cid:7)&
Fig. 3: Overview of our framework. We start with a pre-training mixture, which consists of both our own dexterous
manipulation datasets and open-source data. We use this mixture to train our flow matching VLA model, which consists
of a larger VLM backbone and a smaller action expert for processing robot states and actions. The VLM backbone weights
are initialized from PaliGemma [5], providing representations learned from large-scale Internet pre-training. The resulting π
0
model can be used to control multiple robot embodiments with differing action spaces to accomplish a wide variety of tasks.
of more complex and dexterous behaviors, such as tying Ourmodel,whichwedescribeinSectionIV,isbasedonthe
shoelaces [58] or cooking shrimp [17], we show that our PaliGemma vision-language model [5], which we then further
framework can learn very long tasks, sometimes tens of trainwithourdatamixture.ToturnthebasePaliGemmaVLM
minutes in length, for behaviors that combine both physical intoπ ,weaddactionoutputsthatuseflowmatching[32,28]
0
dexterity and combinatorial complexity. For example, our to generate continuous action distributions. We describe this
laundryfoldingtaskrequirestherobottomanipulateavariety design in detail in the following section. Note that we use
of clothing items that can start in any configuration, and fold PaliGemma for convenience and because of its comparatively
multiple items in sequence. Our table bussing task requires small size (which is useful for real-time control), but our
discerning the class of novel objects (trash or dishes). We framework is compatible with any base pre-trained VLM.
show that a single cross-embodiment model can be used as
the base model for these tasks. To our knowledge, our work IV. THEπ
0
MODEL
demonstrates the longest dexterous tasks in the end-to-end
The π model, illustrated in Figure 3, consists primarily
robot learning literature. 0
of a language model transformer backbone. Following the
standard late fusion VLM recipe [3, 11, 30], image encoders
III. OVERVIEW
embed the robot’s image observations into the same em-
We provide an outline of our model and training procedure bedding space as language tokens. We further augment this
in Figure 3. In our training framework, we first assemble backbonewithrobotics-specificinputsandoutputs—namely,
a pre-training mixture consisting of a weighted combination proprioceptive state and robot actions. π 0 uses conditional
of our own dexterous manipulation datasets (Section V-C), flow matching [28, 32] to model the continuous distribution
collected on 7 different robot configurations for 68 different of actions. Flow matching provides our model with high
tasks, and the entire OXE dataset [10], which contains data precision and multimodal modeling capability, making it es-
from22robots.Thepre-trainingphase(SectionV-A)alsouses pecially well suited to high-frequency dexterous tasks. Our
diverse language labels, combining task names and segment architecture is inspired by Transfusion [59], which trains a
annotations (fine-grained labels for sub-trajectories, typically single transformer using multiple objectives, with tokens1
about 2 seconds in length). The purpose of the pre-training corresponding to continuous outputs supervised via a flow
phase is to train a base model that exhibits broad capabilities matching loss and tokens corresponding to discrete outputs
and generalization, but is not necessarily specialized for high supervised via a cross-entropy loss. Building on Transfusion,
performance on any one task. This base model can follow we additionally found that using a separate set of weights
language commands and perform a variety of tasks at rudi- for the robotics-specific (action and state) tokens led to an
mentary proficiency. For complex and dexterous tasks, we improvement in performance. This design is analogous to a
then employ a post-training procedure (Section V-A), which mixtureofexperts[45,25,12,16]withtwomixtureelements,
uses high-quality curated data to adapt the model to specific where the first element is used for image and text inputs, and
downstream tasks. We study both efficient post-training with
small to moderate amounts of data, and high-quality post- 1Inthispaper,weusetheword“token”torefertoaninput/outputslotalong
the sequence dimension, whether the slot corresponds to a discrete variable
trainingwithlargerdatasetsforcomplextaskssuchaslaundry
(e.g., a language token) or a continuous variable (e.g., an image patch or a
folding and mobile manipulation. robotaction).

--- Page 5 ---
thesecondisusedforrobotics-specificinputsandoutputs.We Non-VLM baseline model. In addition to our main VLA
refer to the second set of weights as the action expert. model, we also trained a similar baseline model that did not
Formally, we want to model the data distribution p(A |o ), useaVLMinitializationforablationexperiments.Thismodel,
t t
where A = [a ,a ,...,a ] corresponds to an action whichwerefertoasπ -small,has470Mparameters,doesnot
t t t+1 t+H−1 0
chunk offutureactions(weuseH =50forourtasks),ando useVLMinitialization,andhasanumberofsmalldifferences
t
is an observation. The observation consists of multiple RGB that we found to be helpful for training on our data without
images, a language command, and the robot’s proprioceptive VLM initialization, which are summarized in Appendix C.
state, such that o = [I1,...,In,ℓ ,q ], where Ii is ith image Thismodelisusedinourcomparisonstoevaluatethebenefits
t t t t t t
(with 2 or 3 images per robot), ℓ is a sequence of language of incorporating VLM pertaining.
t
tokens, and q is a vector of joint angles. The images Ii
and state q are
t
encoded via corresponding encoders and then
t V. DATACOLLECTIONANDTRAININGRECIPE
t
projectedviaalinearprojectionlayerintothesameembedding Broadly capable robot foundation models require not only
space as the language tokens. an expressive and powerful architecture, but also the right
For each action a in the action chunk A , we have a dataset and, more importantly, the right training recipe. In
t′ t
corresponding action token that we feed through the action the same way that LLM training is typically divided into
expert.Duringtraining,wesupervisetheseactiontokensusing pre-training and post-training phases, we employ a multi-
a conditional flow matching loss [28, 32], stage training procedure for our model. The goal of the pre-
training phase is to expose the model to a diverse range of
Lτ(θ)=E ||v (Aτ,o )−u(Aτ|A )||2,
p(At|ot),q(Aτ t |At) θ t t t t tasks so that it can acquire broadly applicable and general
where subscripts denote robot timesteps and superscripts physical capabilities, while the goal of the post-training phase
denote flow matching timesteps, with τ ∈ [0,1]. Recent is to provide the model with the ability to skillfully and
work in high-resolution image [14] and video [38] synthe- fluently execute the desired downstream task. Because of
sis has shown that flow matching can achieve strong em- this, the requirements for the pre-training and post-training
pirical performance when combined with a simple linear- datasets are distinct: the pre-training dataset should cover
Gaussian (or optimal transport) probability path [28], given as many tasks as possible, and within each of those tasks
by q(Aτ|A )=N(τA ,(1−τ)I). In practice, the network shouldcoveradiversityofbehaviors.Thepost-trainingdataset
t t t
is trained by sampling random noise ϵ∼N(0,I), computing should instead cover behaviors that are conducive to effective
the “noisy actions” Aτ =τA +(1−τ)ϵ, and then training task execution, which should exhibit a consistent and fluent
t t
thenetworkoutputsv (Aτ,o )tomatchthedenoisingvector strategy.Intuitively,thediverse(butlowerquality)pre-training
θ t t
field u(Aτ|A ) = A − ϵ. The action expert uses a full data allows the model to recover from mistakes and handle
t t t
bidirectional attention mask, so that all action tokens attend highly varied situations, which might not otherwise occur in
to each other. During training, we sample the flow matching thehigh-qualitypost-trainingdata,whilethepost-trainingdata
timestep τ from a beta distribution that emphasizes lower teaches the model to perform the task well.
(noisier) timesteps. See Appendix B for more details.
A. Pre-training and post-training
At inference time, we generate actions by integrating the
learnedvectorfieldfromτ =0toτ =1,startingwithrandom
noise A0 ∼ N(0,I). We use the forward Euler integration
t
rule:
Aτ+δ =Aτ +δv (Aτ,o ),
t t θ t t
where δ is the integration step size. We use 10 integration
steps (corresponding to δ = 0.1) in our experiments. Note
that inference can be implemented efficiently by caching
the attention keys and values for the prefix o and only
t
recomputing the suffix corresponding to the action tokens for Fig. 4: Overview of our dataset: The pre-training mixture
each integration step. We provide more details regarding the consists of a subset of OXE [10] and the π dataset. We use
inferenceprocedure,includingtheinferencetimeforeachpart a subset of OXE, which we refer to as OXE Magic Soup
of the model, in Appendix D. [24]. The right figure illustrates the weight of the different
Whileinprincipleourmodelcanbeinitializedfromscratch datasets in the pre-training mixture. The left figure illustrates
or fine-tuned from any VLM backbone, in practice we use their relative sizes as measured by the number of steps.
PaliGemma [5] as our base model. PaliGemma is an open-
source3billionparameterVLMthatoffersaconvenienttrade- We provide an overview of our pre-training mixture in Fig-
off between size and performance. We add 300M parameters ure 4. Since each training example corresponds to a timestep
for the action expert (which is initialized from scratch) for a — i.e., a tuple (o ,A ), — we will quantify data in terms
t t
total of 3.3 billion parameters. We provide a full description of timesteps in this discussion. 9.1% of the training mixture
of the model architecture in Appendix B. consists of open-source datasets, including OXE [10], Bridge

--- Page 6 ---
v2 [52], and DROID [23]. The robots and tasks in these
datasets typically have one or two cameras and use low-
frequency control, between 2 and 10 Hz. However, these
datasets cover a wide range of objects and environments. To
learn dexterous and more complex tasks, we also use 903M
timestepsofdatafromourowndatasets,where106Mstepsare
Bimanual UR5e Bimanual Trossen Bimanual ARX
from single-arm robots and 797M are from dual-arm robots.
This data has 68 tasks, where each task is composed of
complexbehaviors—e.g.,the“bussing”taskinvolvesputting
a wide range of different dishes, cups, and utensils into a
bussing bin, and a wide array of trash items into the garbage.
Note that this definition of task is significantly different from
prior work, which typically uses any combination of noun
UR5e Franka Mobile Trossen Mobile Fibocom
and verb (e.g., “pick up the cup” vs. “pick up the plate”)
to constitute a distinct task. Therefore, the actual range of
Fig. 5: The robots used in our experiments. These include
behaviors in our dataset is significantly broader than this
singleanddual-armmanipulatorswith6-DoFand7-DoFarms,
numberof“tasks”wouldimply.Wediscussthespecificrobots
aswellasholonomicandnonholonomicmobilemanipulators.
and tasks in our dataset in more detail in Section V-C. π is trained jointly on all of these platforms.
0
Since the datasets are somewhat imbalanced in size (e.g.,
the more difficult laundry folding tasks are overrepresented),
we weight each task-robot combination by n0.43, where n UR5e. An arm with a parallel jaw gripper, with a wrist-
is the number of samples for that combination, such that mounted and over-the-shoulder camera, for a total of two
over-represented combinations are down-weighted. The con- camera images and a 7-dimensional configuration and action
figuration vector q t and action vectors a t always have the space.
dimensionality of the largest robot in the dataset (18 in our BimanualUR5e.TwoUR5esetups,foratotalofthreecamera
case, to accommodate two 6-DoF arms, 2 grippers, a mobile images and a 14-dimensional configuration and action space.
base, and a vertically actuated torso). For robots with lower- Franka. The Franka setup has two cameras and an 8-
dimensional configuration and action spaces, we zero-pad the dimensional configuration and action space.
configuration and action vectors. For robots with fewer than BimanualTrossen.Thissetuphastwo6-DoFTrossenViperX
three images, we also mask out the missing image slots. arms in a configuration based on the ALOHA setup [4, 57],
In the post-training phase, we fine-tune our model with a with two wrist cameras and a base camera, and a 14-
smallertask-specificdatasettospecializeittoparticulardown- dimensional configuration and action space.
stream applications. As mentioned previously, our definition Bimanual ARX & bimanual AgileX. This setup uses two
of “task” is fairly broad — e.g., the “bussing” task requires 6-DoF arms, and supports either ARX or AgileX arms, with
manipulatingawiderangeofdifferentobjects.Differenttasks three cameras (two wrist and one base) and a 14-dimensional
require very different datasets, with the simplest of the tasks configuration and action space. This class encompasses two
necessitating only 5 hours and the most complex tasks using distinctplatforms,butwecategorizethemtogetherbecauseof
100 or more hours of data. their similar kinematic properties.
Mobile Trossen & mobile ARX. This setup is based on the
B. Language and high-level policies
Mobile ALOHA [57] platform, with two 6-DoF arms on a
More complex tasks that require semantic reasoning and mobile base, which are either ARX arms or Trossen ViperX
high-levelstrategy,suchastablebussing,canalsobenefitfrom arms. The nonholonomic base adds two action dimensions,
a high-level policy that decomposes high-level tasks (such as for a 14-dimensional configuration and 16-dimensional action
“bus the table”) into more immediate subtasks (such as “pick space. There are two wrist cameras and a base camera. This
up the napkin” or “throw the napkin into the trash”). Since class encompasses two distinct platforms, but we categorize
our model is trained to process language inputs, we can use a them together because of their similar kinematic properties.
high-level VLM to make these semantic inferences, a method MobileFibocom.Two6-DoFARXarmsonaholonomicbase.
that is analogous to LLM/VLM planning methods such as Thebaseaddsthreeactiondimensions(twofortranslationand
SayCan [2]. We use such a high-level policy to assist our one for orientation), for a 14-dimensional configuration and
model with high-level strategy for several of our experimental 17-dimensional action space.
tasks, as we will discuss in Section VI. Wesummarizetheproportionofourdatasetfromeachrobot
in Figure 4.
C. Robot system details
Our dexterous manipulation datasets include 7 different
VI. EXPERIMENTALEVALUATION
robot configurations and 68 tasks. We summarize these plat- Our experimental evaluation consists of out-of-box evalu-
forms in Figure 5, and discuss them below: ation experiments that compare our base (pre-trained) model

--- Page 7 ---
the literature: both VLAs and smaller models that are trained
from scratch on the same pre-training mixture. We evaluate
on the following tasks, visualized in Figure 6, with each task
commandedtothesamebasemodelviaalanguagecommand.
Shirt folding: the robot must fold a t-shirt, which starts
flattened.
Bussingeasy:therobotmustcleanatable,puttingtrashinthe
trash bin and dishes into the dish bin. The score indicates the
number of objects that were placed in the correct receptacle.
Bussinghard:aharderversionofthebussingtask,withmore
objects and more challenging configurations, such as utensils
intentionallyplacedontopoftrashobjects,objectsobstructing
each other, and some objects that are not in the pre-training
dataset.
Grocery bagging: the robot must bag all grocery items, such
Fig. 6: Out-of-box evaluation tasks: To evaluate our base
as potato chips, marshmallows, and cat food.
model,werunitafterpre-trainingonfivetasks:shirtfolding,
Toast out of toaster: the robot removes toast from a toaster.
bussing easy, bussing hard, grocery bagging, and toast
Providingcomparisonsfortheseexperimentsischallenging
out of toaster. The tasks require a combination of dexterous
because very few prior models can operate at this scale. We
manipulation,multi-stagebehaviors,andsemanticrecognition.
compare to OpenVLA [24], a 7B parameter VLA model that
was originally trained on the OXE dataset [10]. We train
OpenVLAonourfullmixture.Thisisaverydifficultmixture
to alternative model designs with direct prompting, as well as for OpenVLA, which does not support action chunking or
detailed fine-tuning experiments that evaluate our model on high-frequency control. We also compare to Octo [50], a
challenging downstream tasks, comparing it to other methods smaller 93M parameter model. While Octo is not a VLA, it
thathavebeenproposedfordexterousmanipulation.Westudy does use a diffusion process to generate actions, providing a
the following research questions: valuablepointofcomparisonforourflowmatchingVLA.We
How well does π 0 perform after pre-training on a variety alsotrainOctoonthesamemixtureasourmodel.Duetotime
oftasksthatarepresentinthepre-trainingdata?Westudy constraints, we were unable to train OpenVLA and Octo for
this question by directly evaluating π 0 , with comparisons to the same number of epochs as our full model. We therefore
other robot foundation models. also compare to a “compute parity” version of our model,
How well does π 0 follow language commands? These which is trained for only 160k steps (as opposed to 700k
experiments compare π 0 to π 0 -small, a smaller version of our stepsforourmainmodel),whichisequaltoorlowerthanthe
modelwithoutVLMinitialization,toevaluateitsperformance numberofstepsprovidedtothebaselines(160kforOpenVLA,
on following language commands. We evaluate with both 320k for Octo). We also include a version of the OpenVLA
human-provided commands and commands specified by a model that we fine-tuned only on the UR5e data, without
high-level VLM policy, as discussed in Section V-B. cross-embodiment training, in the hopes of providing an even
Howdoesπ 0 comparetomethodsthathavebeenproposed stronger baseline on the UR5e tasks. Finally, we include a
specifically for addressing dexterous manipulation tasks? comparison to the π -small model described in Section IV,
0
These experiments study downstream tasks for which we can which can be viewed as a scaled-down version of our model
either fine-tune our model from the pre-trained initialization, without VLM pre-training.
or train it from scratch on task-specific data, comparing to Theevaluationmetricusesanormalizedscoreaveragedover
prior methods that were proposed for dexterous manipulation. 10 episodes per task and method, where an episode receives a
We aim to evaluate both the benefits of our architecture and scoreof1.0forafullsuccess,andafractionalscoreforpartial
our pre-training procedure. success. For example, the score for bussing is the fraction of
Can π 0 be adapted to complex, multi-stage tasks? In our objects that are correctly placed in the proper receptacle. We
finalsetofexperiments,wefine-tuneπ 0 toasetofparticularly describethescoringrubricsinAppendixE.Theresults,shown
complex tasks, including folding laundry and bussing a table. in Figure 7, show that π attains by far the best results across
0
Thesetaskstakebetween5and20minutestocomplete.Some theboardonalltheout-of-boxtasks,withnearperfectsuccess
require guidance from a high-level policy. rates on shirt folding and the easier bussing tasks, and large
improvements over all baselines. The “parity” version of π ,
0
A. Evaluating the base model
which is trained for only 160k steps, still outperforms all the
In our first set of experiments, we evaluate the model after baselines,andevenπ -smalloutperformsOpenVLAandOcto.
0
pre-training on our full mixture, without any post-training, OpenVLA struggles on these tasks because its autoregressive
to evaluate how well our base model can perform a variety discretizationarchitecturedoesnotsupportactionchunks.The
of tasks. We compare to other robot foundation models in UR5e-only OpenVLA model performs better, but is still far

--- Page 8 ---
1.0
0.8
0.6
0.4
0.2
0.0
Shirt Folding Bussing Easy Bussing Hard Grocery Bagging Toast
(Bi-ARX) (UR5e) (UR5e) (UR5e) (Bi-Trossen)
ssergorP
ksaT
egarevA
D P i e r r e f c o t r m P a r n o c m e p t A i c n r g o s ( s O u T t a - s o k f s -Box) 0 0(parity) O O p p e e n n V V L L A A (UR5e only)
0 small Octo
Fig. 8: The tasks in our language evaluation. We evaluate
our model on 3 different language-conditioned tasks, each of
which requires following a sequence of intermediate language
commands. The tasks involve bussing a table (top) to put
dishes in a bin and garbage in a trash bin, setting a table
Fig.7:Out-of-boxevaluationresults:Weevaluateπ 0 trained (middle)bytakingitemsoutofabin,andpackingashopping
for the full 700k steps, a version trained for 160k steps that bag (bottom).
matchesthenumberofupdatesforbaselinemodels,π -small,
0
and three baselines: OpenVLA and Octo trained on all of our
data, and OpenVLA trained only on the UR5e tasks (which
task consists of numerous such segments. The tasks in this
we found to work better on UR5e tasks). Across all tasks
evaluation consist of:
and all comparisons, even the “parity” version of our model
Bussing: the robot must clean a table, placing dishes and
outperforms all baselines, and the full version of our model
cutlery in a bin, and trash into a trash bin.
achieves the best results by a large margin.
Table setting: the robot must take out items from a bin to set
a table, including a place mat, dishes, silverware, napkin, and
cups, and adjust them according to language instructions.
belowtheperformanceofπ .Octodoessupportactionchunks,
0 Grocery bagging:therobotmustpackgroceryitems,suchas
buthasacomparativelylimitedrepresentationalcapacity.This
bagsofcoffeebeans,barley,marshmallow,seaweed,almonds,
comparison illustrates the importance of combining large,
spaghetti, and cans into a bag.
expressive architectures with the ability to model complex
In Figure 8, we show the language-conditioned tasks in our
distributions via flow matching or diffusion. Additionally, the
evaluation and present the evaluation results. We evaluate five
comparison to π -small illustrates the importance of incor-
0 different conditions. π -flat (and π -small-flat) corresponds
0 0
porating VLM pre-training. Unfortunately, it is hard to make
to directly command the model with the task description
this last comparison fair: π -small uses fewer parameters, but
0 (e.g.,“bagthegroceries”),withoutintermediatelanguagecom-
largermodelsaredifficulttousewithoutpre-training.Overall,
mands.π -human(andπ -small-human)providesintermediate
0 0
these experiments show that π provides a powerful pre-
0 step commands (e.g., which object to pick and where to place
trained model with the ability to effectively perform a variety
it)fromanexperthumanuser.Theseconditionsevaluateeach
oftaskswithavarietyofrobots,withmuchbetterperformance
model’s ability to follow more detailed language commands:
than prior models.
while these intermediate commands provide considerable in-
formation for how to perform the task, the model must be
B. Following language commands abletounderstandandfollowthosecommandstobenefitfrom
them. Finally, π -HL evaluates π with high-level commands
In the next set of experiments, we fine-tune the base π 0 0
0
provided by a high-level VLM, as discussed in Section V-B.
model to follow language commands in a set of evaluation
Thisconditionisalsoautonomous,withoutanyhumanexpert.
domains. We compare this fine-tuned π model with the π -
0 0
The results in Figure 9, averaging over 10 trials per
small model described in Section IV, which we found to
task, show that the language following accuracy of π is
be the strongest baseline in the previous section. Recall that 0
significantly better than that of π -small. This suggests a
π -small does not use a VLM initialization. This experi- 0
0
significant improvement from the larger pre-trained VLM
ment therefore aims to measure how much VLM pre-training
initialization. This capability translates to an improvement
boosts our model’s ability to follow language instructions.
in performance with expert human guidance (π -human) and
Note that π -small is also a significantly smaller model — 0
0
with high-level model guidance (π -HL). The results indicate
unfortunately,itisdifficulttoremovethisconfounder,because 0
that π ’s language following ability directly translates into
VLM initialization serves both to make it practical to train 0
better autonomous performance on complex tasks with high-
a much larger model without overfitting, and to improve
level guidance.
language instruction following. We nonetheless hope that this
experiment sheds light on the language capabilities of π .
0
C. Learning new dexterous tasks
The language instructions for each task consist of objects to
pick up and locations to place those objects, with language- In the next set of experiments, we evaluate our model on
labeled segments that are about 2 seconds in length. Each full new tasks that differ significantly from the pre-training data,

--- Page 9 ---
Fig. 9: Language evaluation. We compare “flat” versions of
ourpolicies,−flat,whichreceiveonlytheoveralltaskcom-
mand (e.g., “bag the groceries”) with a method that receives
intermediate commands from a human expert, −human, or a
Fig. 10: Fine-tuning evaluation tasks: We fine-tune our
high-levelVLMpolicy,−HL.Wealsocompareourmodeltoa
model to a variety of downstream tasks that are distinct from
small non-VLM variant under the “expert” condition, π and
0 the tasks seen in pre-training. Our tasks represent a range of
π -small,intermsoflanguagefollowingaccuracy.Theresults
0 similarity from the pre-training tasks, with tasks that are most
show a significant improvement with π from intermediate
0 similartopre-training(stackbowlsandtowelfolding),atask
language commands provided by a human expert and to a
that introduces an unseen new element (a microwave), and
lesser degree by an autonomous high-level policy. Notably,
tasks that require new motions and new object types (Franka
due to π -small’s limited language following ability, overall it
0 items in drawer and paper towel replacement).
does not gain with the addition of a high-level expert.
requiring entirely new behaviors. For these evaluations, we models (rather than the architectures), we use the publicly
fine-tune the model using various amounts of data for each available pre-trained checkpoints for these models, which are
new task. While each task is new, we partition the tasks into trainedonOXE[10],andthenfine-tunethemtoeachtask.We
“tiers” depending on how much they differ from tasks in the also compare to ACT [57] and Diffusion Policy [9], which
pre-training data. The tasks, shown in Figure 10, are: are designed specifically for learning dexterous tasks from
UR5e stack bowls. This task requires stacking bowls, with smaller datasets. ACT and Diffusion Policy are trained only
four bowls of different sizes. Since this task requires grasping on the fine-tuning datasets, which are of similar size to the
and moving dishes like the bussing task in the pre-training individual datasets used in the ACT and Diffusion Policy
data, we place it in the “easy” tier. The training data contains experiments [9, 57]. We evaluate π by fine-tuning from our
0
a variety of bowls, and the evaluations use a mix of seen and pre-trained base model, as well as by training from scratch.
unseen bowls. Thiscomparisonismeanttoevaluatetheindividualbenefitsof
Towel folding. This task requires folding a towel. Since this theπ 0 architectureandourpre-trainingprocedure.Wehypoth-
is similar to shirt folding, which is present in pre-training, we esize that the π 0 architecture with VLM initialization should
place it in the “easy” tier. already provide a stronger starting point for the individual
Tupperware in microwave. This task requires opening a tasks,whilethepre-trainingprocedureshouldfurtherimprove
microwave, putting a plastic container inside it, and closing its performance, especially with smaller fine-tuning datasets.
it. The containers come in different shapes and colors, and Figure 11 shows the performance across all of the tasks for
the evaluations use a mix of seen and unseen containers. The a variety of methods, averaging over 10 trials per task, with
container manipulation resembles pre-training data, but the differentamountsoffine-tuningdataoneachtask.Weinclude
microwave is not found in pre-training. allofthebaselinesonthestackbowlsandTupperwareinmi-
Papertowelreplacement.Thistaskrequiresremovinganold crowave tasks. Since OpenVLA and Octo attain significantly
cardboardpapertoweltubefromaholderandreplacingitwith worse performance, we only run these for one of the dataset
a fresh paper towel roll. Because no such items are found in sizes, due to the time cost of evaluating so many models in
pre-training, we consider this “hard.” therealworld.Theresultsshowthatπ generallyoutperforms
0
Frankaitemsindrawer.Thistaskrequiresopeningadrawer, other methods. Interestingly, the strongest prior models are
packingitemsintoadrawer,andclosingit.Becausethereisno the ones that are trained entirely from scratch on the target
similartaskwiththeFrankarobotinpre-training,weconsider tasks,suggestingthatleveragingpre-traininginthesedomains
this “hard.” presents a major challenge for prior approaches. While the 5-
We compare our model after fine-tuning both to Open- hour policy for π on the Tupperware task performs similarly
0
VLA [24] and Octo [50], which also employ a pre-training to the baselines, the 1-hour version is significantly better. As
andfine-tuningrecipe.Sinceouraimistoevaluatethespecific expected, pre-training leads to larger improvement for tasks

--- Page 10 ---
1.0
0.5
0.0
1 5 10
Fine-Tuning Data (Hours)
ssergorP
ksaT
egarevA
Average Across All Tasks
1.0
0.5
0.0
111 555 111000
Fine-Tuning Data (Hours)
ssergorP
ksaT
egarevA
Paper Towel Replacement
(Bi-UR5e)
1.0
0.5
0.0
111 555 111000
Fine-Tuning Data (Hours)
ssergorP
ksaT
egarevA
Items in Drawer
(Franka)
1.0
0.5
0.0
111 555 111000
Fine-Tuning Data (Hours)
ssergorP
ksaT
egarevA
Towel Folding
(Bi-ARX)
1.0
0.5
0.0
1111 555555 11110000
Fine-Tuning Data (Hours)
ssergorP
ksaT
egarevA
Stack Bowls
(UR5e)
1.0
0.5
0.0
1111 555555 11110000
Fine-Tuning Data (Hours)
ssergorP
ksaT
egarevA
0 DP OpenVLA
0(scratch) Octo ACT
Tupperware in Microwave
(Bi-ARX)
Fig. 11: Fine-tuning with varying amounts of data. π can learn some easier tasks even with smaller amounts of data, and
0
the pre-trained model often attains a larger improvement over the model trained from scratch.
that are more similar to the pre-training data, though the pre- of varying shapes and sizes, and perform complex dexterous
trained model is frequently better than the non-pre-trained motions, such as twisting the gripper to pick up large plates
model, sometimes by as much as 2x. and carefully grasping thin, delicate items such as glasses.
Therobotmusthandledenseclutterandintelligentlysequence
D. Mastering complex multi-stage tasks
various behaviors — for example, to clean off a plate with
In our final set of experiments, we tackle a range of trash, it must first pick up the plate, then shake its contents
challenging multi-stage tasks via a combination of fine-tuning into the garbage, and then place the plate in the bin. This task
and language. For some of these tasks, data is present in pre- is not present in pre-training.
training,butfine-tuningisrequiredtoattainmastery.Forsome,
Box building: The robot has to assemble a cardboard box
no data is present in pre-training. The tasks in this evaluation,
that starts in a flattened state. This task presents a number of
shown in Figure 12, are:
major challenges: the box needs to bent in the right way, and
Laundry folding: This task requires a static (non-mobile) bi-
the robot needs to hold down parts of the box while folding
manual system to fold articles of clothing. The clothing items
others,utilizingbotharmsandeventhesurfaceofthetableto
start in a randomized crumpled state in a bin, and the goal is
brace during folding motions. The robot might need to retry
to take out the item, fold it, and place it on top of a stack of
some folds, requiring a reactive and intelligent strategy. This
previously folded items. The randomized initial configuration
task is not present in pre-training.
of the crumpled laundry presents a major challenge, since the
To-gobox:Thistaskrequiresmovingseveralfooditemsfrom
policy needs to generalize to any configuration. This task is
a plate into a to-go box, requiring packing the items into the
present in pre-training.
box so that they do not stick out, and then closing the box
Mobile laundry: Here,the Fibocommobile robotin Figure5
with both arms. This task is not present in pre-training.
hastofoldlaundry,facingmanyofthesamechallengeswhile
controlling orientation and translation. This task is present in Packing eggs: The robot needs to take six eggs out of a
pre-training. bowl and pack them into an egg carton, and then close the
Dryerunloading:Here,theFibocommobilerobothastotake carton. The eggs need to be grasped in a manner appropriate
laundry out of a dryer and place it into a hamper. This task is to their pose inside the bowl, and then placed into open slots
present in pre-training. in the carton. This presents challenges due to the egg shape,
Table bussing: This task requires bussing a table with a slipperiness, and the need for careful placement. Closing the
diverse array of novel objects in a clutter scene, presenting box requires the use of both arms. This task is not present in
a much greater challenge than the benchmark in our out-of- pre-training.
box evaluation: the policy must generalize to unseen objects The results, showing average scores per task over 10 trials,

--- Page 11 ---
Fig. 12: We evaluate a range of complex and temporally
extended tasks. This includes: folding laundry from a bin
with a stationary (a) or mobile (b) robot, bussing a real
lunch table (c), assembling a box (d), packing eggs into a
carton (e), and packing food into a to-go box (f). These tasks
Fig. 13: Post-training results on complex tasks in terms of
require combining dozens of individual behaviors, such as
average scores over 10 trials. The full pre-trained π model
grasping, stacking, folding, and flattening, generalization to 0
attainsmorethan50%ofthemaximumscoreacrossallofthe
a huge variety of object configurations, and complex physical
tasks, and typically outperforms the ablations, with especially
properties, such as deformable objects or flexible cardboard.
significant improvements on the hardest tasks.
are presented in Figure 13. The scoring rubrics are in Ap-
pendix E. A score of 1.0 represents a perfect execution, while Our empirical evaluation studies tasks that combine dexterity,
partialscorescorrespondtopartiallycompletedtasks(e.g.,0.5 generalization,andtemporallyextendedmulti-stagebehaviors.
indicates that half the objects were bussed correctly). These Our model incorporates Internet-scale vision-language model
tasks are very difficult, and we were not able to solve them (VLM) pre-training with flow matching for representing com-
with other methods. We therefore use these tasks to compare plex high-frequency action chunks. Our pre-training mixture
to ablations of our approach, evaluating π after pre-training consists of 10,000 hours of dexterous manipulation data from
0
and fine-tuning, out of the box after pre-training only (“out- 7 different robot configurations and 68 tasks, in addition
of-box”), and training on the fine-tuning data without any to large amounts of previously collected robot manipulation
pre-training (“scratch”). The results show that π can solve data from OXE [10], DROID [23], and Bridge [52]. To our
0
many of these tasks, with our full pre-training and fine-tuning knowledge, this represents the largest pre-training mixture
recipe performing best across the board. Note that many of ever used for a robot manipulation model. Our fine-tuning
these more difficult tasks show a very large improvement experiments include over 20 tasks, where we show that our
fromusingthepre-trainedmodel,indicatingthatpre-trainingis modeloutperformsavarietyofbaselines,includingpriorVLA
especially useful with harder tasks. The absolute performance models [24] and models designed specifically for dexterous
of π varies across the tasks, likely due to differences in task manipulation [57, 9]. We also examine how our post-training
0
difficulty and the degree to which the tasks are represented recipe can enable highly complex tasks, such as folding mul-
in pre-training. We recommend that readers watch the task tiple articles of clothing from arbitrary initial configurations
videos on the accompanying website for a more complete or assembling boxes.
impression of these tasks and their complexity. We believe Our framework broadly resembles the training procedures
thatthislevelofautonomousperformanceonsuchchallenging employed for large language models, which typically consist
tasks represents a new state of the art in dexterous robot of pre-training a base model on very large datasets scraped
manipulation with learned policies. fromtheweb,followedbyapost-trainingprocedurethataims
to “align” the model to enable it to follow instructions and
VII. DISCUSSION,LIMITATIONS,ANDFUTUREWORK
perform user commands. It is generally recognized that most
We presented a framework for training a robot founda- of the “knowledge” in such models is acquired in the pre-
tion model, which we refer to as π , that consists of pre- training phase, while the post-training phase serves to tell
0
training on highly diverse data, followed by either out-of- the model how it should leverage that knowledge to fulfill
box evaluation or fine-tuning to complex downstream tasks. user commands. Our experiments imply that an analogous

--- Page 12 ---
phenomenon might take place with robot foundation models, Advances in neural information processing systems, 35:
where pre-trained models have some zero-shot capabilities, 23716–23736, 2022.
but complex tasks like laundry following require fine-tuning [4] Jorge Aldaco, Travis Armstrong, Robert Baruch,
with high-quality data. Training on only this high-quality data Jeff Bingham, Sanky Chan, Kenneth Draper, De-
results in a brittle model that does not reliably recover from bidatta Dwibedi, Chelsea Finn, Pete Florence, Spencer
mistakes, while running the pre-trained model in zero shot Goodrich, et al. Aloha 2: An enhanced low-cost
does not always exhibit the fluent strategies demonstrated in hardware for bimanual teleoperation. arXiv preprint
the post-training data. arXiv:2405.02292, 2024.
We hope that our results will serve as a stepping stone to- [5] Lucas Beyer, Andreas Steiner, Andre´ Susano Pinto,
wardgeneralandbroadlyapplicablerobotfoundationmodels. Alexander Kolesnikov, Xiao Wang, Daniel Salz, Maxim
Our experiments suggest that such models may soon be a Neumann, Ibrahim Alabdulmohsin, Michael Tschannen,
reality, but there are a number of limitations and ample room Emanuele Bugliarello, et al. Paligemma: A versatile 3b
for future work. First, our experiments do not yet provide a vlmfortransfer. arXivpreprintarXiv:2407.07726,2024.
comprehensive understanding of how the pre-training datasets [6] Homanga Bharadhwaj, Jay Vakil, Mohit Sharma, Ab-
shouldbecomposed:wecombinedalldataavailabletous,but hinav Gupta, Shubham Tulsiani, and Vikash Kumar.
understanding what type of data is more helpful to add and RoboAgent: Generalization and efficiency in robot ma-
how it should be weighted remains an open problem. Not all nipulationviasemanticaugmentationsandactionchunk-
tasks in our evaluation work reliably, and it remains unclear ing. In2024IEEEInternationalConferenceonRobotics
how to predict how much and what kind of data is needed and Automation (ICRA), pages 4788–4795. IEEE, 2024.
to attain near-perfect performance. Finally, it remains to be [7] Anthony Brohan, Noah Brown, Justice Carbajal, Yevgen
seen how much positive transfer there is in combining highly Chebotar,XiChen,KrzysztofChoromanski,TianliDing,
diverse data, particularly from different tasks and different Danny Driess, Avinava Dubey, Chelsea Finn, Pete Flo-
robots: although our results suggest that universal pre-trained rence,ChuyuanFu,MontseGonzalezArenas,Keerthana
robot foundation models might become a reality, it is left for Gopalakrishnan, Kehang Han, Karol Hausman, Alexan-
future work to understand whether this universality extends derHerzog,JasmineHsu,BrianIchter,AlexIrpan,Nikhil
to much more distinct domains, such as autonomous driving, Joshi, Ryan Julian, Dmitry Kalashnikov, Yuheng Kuang,
navigation, and legged locomotion. Isabel Leal, Lisa Lee, Tsang-Wei Edward Lee, Sergey
Levine, Yao Lu, Henryk Michalewski, Igor Mordatch,
ACKNOWLEDGEMENTS Karl Pertsch, Kanishka Rao, Krista Reymann, Michael
Ryoo, Grecia Salazar, Pannag Sanketi, Pierre Sermanet,
We thank Laura Smith and Dibya Ghosh for feedback on
JaspiarSingh,AnikaitSingh,RaduSoricut,HuongTran,
thepaperandassistancewithfiguresandvideos,PhilipClark,
Vincent Vanhoucke, Quan Vuong, Ayzaan Wahid, Stefan
Kelly Sims, and Saunaz Moradi for feedback on writing, and
Welker, Paul Wohlhart, Jialin Wu, Fei Xia, Ted Xiao,
Evan Pokrandt, Joakim Keussen, Dan Philibin, Eitan Penner,
Peng Xu, Sichun Xu, Tianhe Yu, and Brianna Zitkovich.
Adam Lisagor, and Greg Miller for help with illustrations,
Rt-2:Vision-language-actionmodelstransferwebknowl-
design,andvideos.WealsothankLiliYuforhelpfultechnical
edgetoroboticcontrol.arXivpreprintarXiv:2307.15818,
discussion. We are tremendously grateful to all of the robot
2023.
operatorsfortirelesslycollectingrobotmanipulationdata.For
[8] Serkan Cabi, Sergio Go´mez Colmenarejo, Alexander
a full contribution statement, see Appendix A.
Novikov, Ksenia Konyushkova, Scott Reed, Rae Jeong,
KonradZolna,YusufAytar,DavidBudden,MelVecerik,
REFERENCES
et al. Scaling data-driven robotics with reward sketch-
[1] Josh Achiam, Steven Adler, Sandhini Agarwal, Lama ing and batch reinforcement learning. arXiv preprint
Ahmad, Ilge Akkaya, Florencia Leoni Aleman, Diogo arXiv:1909.12200, 2019.
Almeida, Janko Altenschmidt, Sam Altman, Shyamal [9] Cheng Chi, Zhenjia Xu, Siyuan Feng, Eric Cousineau,
Anadkat, et al. Gpt-4 technical report. arXiv preprint YilunDu,BenjaminBurchfiel,RussTedrake,andShuran
arXiv:2303.08774, 2023. Song. Diffusion policy: Visuomotor policy learning via
[2] Michael Ahn, Anthony Brohan, Noah Brown, Yevgen action diffusion. The International Journal of Robotics
Chebotar, Omar Cortes, Byron David, Chelsea Finn, Research, page 02783649241273668, 2023.
Chuyuan Fu, Keerthana Gopalakrishnan, Karol Haus- [10] OX-Embodiment Collaboration, A Padalkar, A Pooley,
man,etal. Doasican,notasisay:Groundinglanguage A Jain, A Bewley, A Herzog, A Irpan, A Khazatsky,
inroboticaffordances. arXivpreprintarXiv:2204.01691, A Rai, A Singh, et al. Open X-Embodiment: Robotic
2022. learning datasets and RT-X models. arXiv preprint
[3] Jean-Baptiste Alayrac, Jeff Donahue, Pauline Luc, An- arXiv:2310.08864, 1(2), 2023.
toineMiech,IainBarr,YanaHasson,KarelLenc,Arthur [11] DannyDriess,FeiXia,MehdiSMSajjadi,CoreyLynch,
Mensch, Katherine Millican, Malcolm Reynolds, et al. Aakanksha Chowdhery, Brian Ichter, Ayzaan Wahid,
Flamingo:avisuallanguagemodelforfew-shotlearning. JonathanTompson,QuanVuong,TianheYu,etal. Palm-

--- Page 13 ---
e: An embodied multimodal language model. arXiv based robotic manipulation. In Conference on robot
preprint arXiv:2303.03378, 2023. learning, pages 651–673. PMLR, 2018.
[12] Nan Du, Yanping Huang, Andrew M Dai, Simon Tong, [23] Alexander Khazatsky, Karl Pertsch, Suraj Nair, Ash-
Dmitry Lepikhin, Yuanzhong Xu, Maxim Krikun, Yanqi win Balakrishna, Sudeep Dasari, Siddharth Karam-
Zhou,AdamsWeiYu,OrhanFirat,etal. Glam:Efficient cheti, Soroush Nasiriany, Mohan Kumar Srirama,
scaling of language models with mixture-of-experts. In Lawrence Yunliang Chen, Kirsty Ellis, et al. DROID: A
International Conference on Machine Learning, pages large-scale in-the-wild robot manipulation dataset. arXiv
5547–5569. PMLR, 2022. preprint arXiv:2403.12945, 2024.
[13] Frederik Ebert, Yanlai Yang, Karl Schmeckpeper, [24] Moo Jin Kim, Karl Pertsch, Siddharth Karamcheti, Ted
Bernadette Bucher, Georgios Georgakis, Kostas Dani- Xiao, Ashwin Balakrishna, Suraj Nair, Rafael Rafailov,
ilidis, Chelsea Finn, and Sergey Levine. Bridge data: EthanFoster,GraceLam,PannagSanketi,etal.Openvla:
Boosting generalization of robotic skills with cross- An open-source vision-language-action model. arXiv
domaindatasets. arXivpreprintarXiv:2109.13396,2021. preprint arXiv:2406.09246, 2024.
[14] Patrick Esser, Sumith Kulal, Andreas Blattmann, Rahim [25] Dmitry Lepikhin, HyoukJoong Lee, Yuanzhong Xu, De-
Entezari, Jonas Mu¨ller, Harry Saini, Yam Levi, Dominik hao Chen, Orhan Firat, Yanping Huang, Maxim Krikun,
Lorenz, Axel Sauer, Frederic Boesel, et al. Scaling Noam Shazeer, and Zhifeng Chen. Gshard: Scaling
rectified flow transformers for high-resolution image giantmodelswithconditionalcomputationandautomatic
synthesis. In Forty-first International Conference on sharding. arXiv preprint arXiv:2006.16668, 2020.
Machine Learning, 2024. [26] Sergey Levine, Peter Pastor, Alex Krizhevsky, Julian
[15] Haritheja Etukuru, Norihito Naka, Zijin Hu, Seung- Ibarz, and Deirdre Quillen. Learning hand-eye coor-
jae Lee, Julian Mehu, Aaron Edsinger, Chris Pax- dination for robotic grasping with deep learning and
ton, Soumith Chintala, Lerrel Pinto, and Nur Muham- large-scale data collection. The International journal of
mad Mahi Shafiullah. Robot utility models: General robotics research, 37(4-5):421–436, 2018.
policies for zero-shot deployment in new environments. [27] Yujia Li, David Choi, Junyoung Chung, Nate Kushman,
arXiv preprint arXiv:2409.05865, 2024. Julian Schrittwieser, Re´mi Leblond, Tom Eccles, James
[16] William Fedus, Barret Zoph, and Noam Shazeer. Switch Keeling, Felix Gimeno, Agustin Dal Lago, Thomas Hu-
transformers: Scaling to trillion parameter models with bert, Peter Choy, Cyprien de Masson d’Autume, Igor
simple and efficient sparsity. Journal of Machine Learn- Babuschkin, Xinyun Chen, Po-Sen Huang, Johannes
ing Research, 23(120):1–39, 2022. Welbl, Sven Gowal, Alexey Cherepanov, James Molloy,
[17] Zipeng Fu, Tony Z. Zhao, and Chelsea Finn. Mobile Daniel J. Mankowitz, Esme Sutherland Robson, Push-
aloha:Learningbimanualmobilemanipulationwithlow- meet Kohli, Nando de Freitas, Koray Kavukcuoglu, and
cost whole-body teleoperation. In Conference on Robot Oriol Vinyals. Competition-level code generation with
Learning (CoRL), 2024. alphacode. Science, 378(6624):1092–1097, 2022.
[18] Abhinav Gupta, Adithyavairavan Murali, [28] YaronLipman,RickyTQChen,HeliBen-Hamu,Maxim-
Dhiraj Prakashchand Gandhi, and Lerrel Pinto. ilian Nickel, and Matt Le. Flow matching for generative
Robot learning in homes: Improving generalization and modeling. arXiv preprint arXiv:2210.02747, 2022.
reducing dataset bias. Advances in neural information [29] Bingchen Liu, Ehsan Akhgari, Alexander Visheratin,
processing systems, 31, 2018. AleksKamko,LinmiaoXu,ShivamShrirao,JoaoSouza,
[19] Wanggui He, Siming Fu, Mushui Liu, Xierui Wang, SuhailDoshi,andDaiqingLi. Playgroundv3:Improving
Wenyi Xiao, Fangxun Shu, Yi Wang, Lei Zhang, Zhelun text-to-image alignment with deep-fusion large language
Yu, Haoyuan Li, et al. Mars: Mixture of auto-regressive models. arXiv preprint arXiv:2409.10695, 2024.
models for fine-grained text-to-image synthesis. arXiv [30] Haotian Liu, Chunyuan Li, Qingyang Wu, and Yong Jae
preprint arXiv:2407.07614, 2024. Lee. Visual instruction tuning. Advances in neural
[20] Jonathan Ho, Ajay Jain, and Pieter Abbeel. Denoising information processing systems, 36, 2024.
diffusionprobabilisticmodels. Advancesinneuralinfor- [31] Peiqi Liu, Yaswanth Orru, Jay Vakil, Chris Paxton, Nur
mation processing systems, 33:6840–6851, 2020. Muhammad Mahi Shafiullah, and Lerrel Pinto. Ok-
[21] John Jumper, Richard Evans, Alexander Pritzel, Tim robot:Whatreallymattersinintegratingopen-knowledge
Green, Michael Figurnov, Olaf Ronneberger, Kathryn models for robotics. arXiv preprint arXiv:2401.12202,
Tunyasuvunakool, Russ Bates, Augustin Zˇ´ıdek, Anna 2024.
Potapenko, et al. Highly accurate protein structure [32] Qiang Liu. Rectified flow: A marginal preserv-
prediction with alphafold. Nature, 596(7873):583–589, ing approach to optimal transport. arXiv preprint
2021. arXiv:2209.14577, 2022.
[22] Dmitry Kalashnikov, Alex Irpan, Peter Pastor, Julian [33] Ajay Mandlekar, Yuke Zhu, Animesh Garg, Jonathan
Ibarz, Alexander Herzog, Eric Jang, Deirdre Quillen, Booher, Max Spero, Albert Tung, Julian Gao, John
Ethan Holly, Mrinal Kalakrishnan, Vincent Vanhoucke, Emmons,AnchitGupta,EmreOrbay,etal. RoboTurk:A
et al. Scalable deep reinforcement learning for vision- crowdsourcingplatformforroboticskilllearningthrough

--- Page 14 ---
imitation. InConferenceonRobotLearning,pages879– Dean. Outrageously large neural networks: The
893. PMLR, 2018. sparsely-gated mixture-of-experts layer. arXiv preprint
[34] Ajay Mandlekar, Soroush Nasiriany, Bowen Wen, Ire- arXiv:1701.06538, 2017.
tiayo Akinola, Yashraj Narang, Linxi Fan, Yuke Zhu, [46] Jascha Sohl-Dickstein, Eric Weiss, Niru
and Dieter Fox. MimicGen: A data generation system Maheswaranathan, and Surya Ganguli. Deep
for scalable robot learning using human demonstrations. unsupervised learning using nonequilibrium
arXiv preprint arXiv:2310.17596, 2023. thermodynamics. In International conference on
[35] Long Ouyang, Jeffrey Wu, Xu Jiang, Diogo Almeida, machine learning, pages 2256–2265. PMLR, 2015.
Carroll Wainwright, Pamela Mishkin, Chong Zhang, [47] Andreas Steiner, Alexander Kolesnikov, Xiaohua Zhai,
Sandhini Agarwal, Katarina Slama, Alex Ray, et al. RossWightman,JakobUszkoreit,andLucasBeyer. How
Training language models to follow instructions with to train your vit? data, augmentation, and regularization
human feedback. Advances in neural information pro- invisiontransformers. arXivpreprintarXiv:2106.10270,
cessing systems, 35:27730–27744, 2022. 2021.
[36] William Peebles and Saining Xie. Scalable diffu- [48] Gemini Team, Rohan Anil, Sebastian Borgeaud, Jean-
sion models with transformers. In Proceedings of the BaptisteAlayrac,JiahuiYu,RaduSoricut,JohanSchalk-
IEEE/CVF International Conference on Computer Vi- wyk, Andrew M Dai, Anja Hauth, Katie Millican, et al.
sion, pages 4195–4205, 2023. Gemini: a family of highly capable multimodal models.
[37] Lerrel Pinto and Abhinav Gupta. Supersizing self- arXiv preprint arXiv:2312.11805, 2023.
supervision: Learning to grasp from 50k tries and 700 [49] GemmaTeam,ThomasMesnard,CassidyHardin,Robert
robot hours. In 2016 IEEE international conference Dadashi, Surya Bhupatiraju, Shreya Pathak, Laurent
on robotics and automation (ICRA), pages 3406–3413. Sifre,MorganeRivie`re,MihirSanjayKale,JulietteLove,
IEEE, 2016. et al. Gemma: Open models based on gemini research
[38] Adam Polyak, Amit Zohar, Andrew Brown, Andros and technology. arXiv preprint arXiv:2403.08295, 2024.
Tjandra,AnimeshSinha,AnnLee,ApoorvVyas,Bowen [50] Octo Model Team, Dibya Ghosh, Homer Walke, Karl
Shi, Chih-Yao Ma, Ching-Yao Chuang, et al. Movie Pertsch, Kevin Black, Oier Mees, Sudeep Dasari, Joey
gen: A cast of media foundation models. arXiv preprint Hejna, Tobias Kreiman, Charles Xu, et al. Octo: An
arXiv:2410.13720, 2024. open-source generalist robot policy. arXiv preprint
[39] Alec Radford, Jong Wook Kim, Chris Hallacy, Aditya arXiv:2405.12213, 2024.
Ramesh, Gabriel Goh, Sandhini Agarwal, Girish Sastry, [51] Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob
Amanda Askell, Pamela Mishkin, Jack Clark, et al. Uszkoreit,LlionJones,AidanNGomez,ŁukaszKaiser,
Learning transferable visual models from natural lan- and Illia Polosukhin. Attention is all you need. In
guage supervision. In International conference on ma- Advances in Neural Information Processing Systems,
chine learning, pages 8748–8763. PMLR, 2021. volume 30, 2017.
[40] Robin Rombach, Andreas Blattmann, Dominik Lorenz, [52] Homer Rich Walke, Kevin Black, Tony Z Zhao, Quan
Patrick Esser, and Bjo¨rn Ommer. High-resolution image Vuong, Chongyi Zheng, Philippe Hansen-Estruch, An-
synthesis with latent diffusion models. In Proceedings dre Wang He, Vivek Myers, Moo Jin Kim, Max Du,
of the IEEE/CVF conference on computer vision and et al. BridgeData v2: A dataset for robot learning at
pattern recognition, pages 10684–10695, 2022. scale. In Conference on Robot Learning, pages 1723–
[41] Chitwan Saharia, William Chan, Saurabh Saxena, Lala 1736. PMLR, 2023.
Li, Jay Whang, Emily L Denton, Kamyar Ghasemipour, [53] Jason Wei, Maarten Bosma, Vincent Y Zhao, Kelvin
Raphael Gontijo Lopes, Burcu Karagol Ayan, Tim Sali- Guu, Adams Wei Yu, Brian Lester, Nan Du, Andrew M
mans,etal. Photorealistictext-to-imagediffusionmodels Dai, and Quoc V Le. Finetuned language models are
with deep language understanding. Advances in neural zero-shot learners. arXiv preprint arXiv:2109.01652,
information processing systems, 35:36479–36494, 2022. 2021.
[42] V Sanh. Distilbert, a distilled version of bert: [54] Jason Wei, Yi Tay, Rishi Bommasani, Colin Raffel, Bar-
Smaller, faster, cheaper and lighter. arXiv preprint ret Zoph, Sebastian Borgeaud, Dani Yogatama, Maarten
arXiv:1910.01108, 2019. Bosma, Denny Zhou, Donald Metzler, et al. Emer-
[43] Nur Muhammad Mahi Shafiullah, Anant Rai, Haritheja gent abilities of large language models. arXiv preprint
Etukuru,YiqianLiu,IshanMisra,SoumithChintala,and arXiv:2206.07682, 2022.
Lerrel Pinto. On bringing robots home. arXiv preprint [55] Junjie Wen, Yichen Zhu, Jinming Li, Minjie Zhu, Kun
arXiv:2311.16098, 2023. Wu, Zhiyuan Xu, Ning Liu, Ran Cheng, Chaomin
[44] Noam Shazeer. Fast transformer decoding: One write- Shen, Yaxin Peng, Feifei Feng, and Jian Tang.
head is all you need. arXiv preprint arXiv:1911.02150, Tinyvla: Towards fast, data-efficient vision-language-
2019. action models for robotic manipulation. arXiv preprint
[45] Noam Shazeer, Azalia Mirhoseini, Krzysztof Maziarz, arXiv:2409.12514, 2024.
Andy Davis, Quoc Le, Geoffrey Hinton, and Jeff [56] Kuan-Ting Yu, Maria Bauza, Nima Fazeli, and Alberto

--- Page 15 ---
Rodriguez. More than a million ways to be pushed. a vector q and action vectors A = [a ,...,a ], (2) an
t t t t+H−1
high-fidelity experimental dataset of planar pushing. In additional MLP for incorporating the flow matching timestep
2016 IEEE/RSJ international conference on intelligent informationτ,and(3)asecond,smallersetofweightsforthe
robots and systems (IROS), pages 30–37. IEEE, 2016. action expert.
[57] TonyZZhao,VikashKumar,SergeyLevine,andChelsea Additional inputs and outputs. The standard PaliGemma
Finn. Learning fine-grained bimanual manipulation with architecturetakesinasequenceofimages[I1,...,In]followed
t t
low-cost hardware. arXiv preprint arXiv:2304.13705, by a language prompt ℓ . We add an input q for the robot’s
t t
2023. proprioceptive state, which is mapped to the transformer
[58] Tony Z Zhao, Jonathan Tompson, Danny Driess, Pete embedding dimension using a linear projection. The final
Florence, Kamyar Ghasemipour, Chelsea Finn, and set of input tokens correspond to the noisy action chunk
Ayzaan Wahid. Aloha unleashed: A simple recipe for Aτ =[aτ,...,aτ ], with the number of tokens equal to
t t t+H−1
robot dexterity. arXiv preprint arXiv:2410.13126, 2024. the action horizon (H = 50 for our tasks). We only use
[59] Chunting Zhou, Lili Yu, Arun Babu, Kushal Tiru- the transformer outputs corresponding to the H noisy actions,
mala, Michihiro Yasunaga, Leonid Shamis, Jacob Kahn, which are decoded into v (Aτ,o ) using a linear projection.
θ t t
XuezheMa,LukeZettlemoyer,andOmerLevy. Transfu- Incorporating the flow matching timestep. The noisy
sion: Predict the next token and diffuse images with one action chunk Aτ is mapped to the transformer’s embedding
t
multi-modal model. arXiv preprint arXiv:2408.11039, dimension using an MLP that also incorporates the flow
2024. matching timestep τ. For each noisy action aτ, the expres-
t′
[60] Minjie Zhu, Yichen Zhu, Jinming Li, Junjie Wen, sion for the corresponding embedding that is fed into the
ZhiyuanXu,NingLiu,RanCheng,ChaominShen,Yaxin transformerisW ·swish(W ·concat(W ·aτ,ϕ(τ))),where
3 2 1 t′
Peng,FeifeiFeng,etal. Scalingdiffusionpolicyintrans- ϕ:R→Rw isasinusoidalpositionalencodingfunction[51],
former to 1 billion parameters for robotic manipulation. W ∈ Rw×d, W ∈ Rw×2w, W ∈ Rw×w, d is the action
1 2 3
arXiv preprint arXiv:2409.14411, 2024. dimension, and w is the embedding dimension (or width) of
the action expert.
APPENDIX
Attentionmask.π usesablockwisecausalattentionmask
0
A. Contributions with3blocks:[I1,...,In,ℓ ],[q ],and[aτ,...,aτ ].Within
t t t t t t+H−1
Theauthorscontributedtothefollowingareas(listedalpha- each block, there is full bidirectional attention, whereas the
betically): tokens in each block cannot attend to the tokens in future
Data and operations: Noah Brown, Michael Equi, Chelsea blocks. The first block includes the input modalities from
Finn, Niccolo Fusai, Lachy Groom, Liyiming Ke, Suraj Nair, PaliGemma’s VLM pre-training, which are prevented from
Lucy Shi, and Anna Walling. attending to future blocks (which include new inputs) to
Evaluationexperiments:KevinBlack,MichaelEqui,Chelsea minimize distribution shift from said pre-training. The robot
Finn, Brian Ichter, Liyiming Ke, Adrian Li-Bell, Suraj Nair, stateq t isitsownblockbecauseitdoesnotchangewitheach
Karl Pertsch, and Lucy Shi. flow matching integration step; preventing it from attending
Modeldesign:KevinBlack,BrianIchter,SergeyLevine,Karl to the final block allows its corresponding keys and values to
Pertsch, Lucy Shi, and Quan Vuong. becachedduringsampling.Thefinalblockcorrespondstothe
Post-training: Michael Equi, Chelsea Finn, Liyiming Ke, noisyactionsAτ t ,whichcanattendtothefullinputsequence.
Adrian Li-Bell, Suraj Nair, and Lucy Shi. Action expert. π 0 is implemented as a single transformer
Pre-training:KevinBlack,DannyDriess,BrianIchter,Sergey with two sets of weights (also known as experts [45]),
Levine, Karl Pertsch, Lucy Shi, and Quan Vuong. where each token is routed to one of the experts; the
Robot hardware:NoahBrown,AdnanEsmail,ChelseaFinn, weights interact only through the transformer’s self-attention
Tim Jones, and Mohith Mothukuri. layers. The images and language prompt, [I1 t ,...,In t ,ℓ t ], are
Robot software: Karol Hausman, Szymon Jakubczak, Sergey routed to the larger VLM backbone, which we initialize
Levine, James Tanner, and Haohuan Wang. from PaliGemma. The inputs not seen during VLM pre-
Training infrastructure: Kevin Black, Michael Equi, Sergey training, [q t ,Aτ t ], are routed to the action expert. PaliGemma
Levine, Adrian Li-Bell, Suraj Nair, Quan Vuong, Haohuan is based on the Gemma 2B [49] language model, which
Wang, and Ury Zhilinsky. uses multi-query attention [44] and a configuration of
Writing and illustration: Kevin Black, Chelsea Finn, Lachy {width=2048, depth=18, mlp dim=16,384, num heads=18,
Groom, Karol Hausman, Brian Ichter, Sergey Levine, and num kv heads=1, head dim=256}. Since the experts interact
Quan Vuong. only in the self-attention layers, width and mlp dim do not
necessarily need to match between experts. To speed up
B. Model Architecture Details
inference (which requires multiple forward passes of the
In this section, we provide a full description of the model actionexpert),wedownsizetheactionexpertto{width=1024,
architecture. We follow the PaliGemma VLM [5] design, mlp dim=4096}, resulting in a parameter count of ∼300M.
with the following differences: (1) additional input and output Sampling the flow matching timestep. The original flow
projectionsfortherobotics-specifictokens,includingthestate matching papers [28, 32] sample the flow matching timestep

--- Page 16 ---
0 s 1
τ
)τ(p
encoder (specifically, the R26-S-32 ResNet-ViT hybrid from
Steiner et al. [47]); (4) The ViT image encoders do not
share weights; (5) The transformer backbone that encodes the
observations (which comes after the ViT image encoders) is
not pre-trained on Internet data; (6) The action expert uses
the DiT architecture [36] rather than the Gemma architecture,
and hence incorporates the flow-matching timestep τ using
AdaLN-Zero layers. Besides this, the models are broadly
similar: both use pre-trained ViT image encoders, both use
separate weights for the observation encoder and the action
expert, both take in the same observation format, and both
perform10stepsofflowmatchingtopredicttheactionchunk.
Fig. 14: Flow matching timestep sampling distribution.
We sample τ from a shifted beta distribution that emphasizes D. Inference
lower timesteps (corresponding to noisier actions), and does Recall that our model takes an observation o =
t
not sample timesteps at all above a cutoff value s. We use [I1,...,In,ℓ ,q ] and the noisy actions Aτ and outputs the
t t t t t
s=0.999 in our experiments. vector field that needs to be integrated to obtain the next
flow matching step, vτ. Each time we predict a new action
t
chunkA ,wemustencodeeachoftheimagesI1,...,In,runa
t t t
from a uniform distribution: τ ∼ U(0,1). Esser et al. [14] forward pass on the tokens corresponding to o , and then run
t
insteadproposesamplingfromalogit-normaldistributionthat 10stepsofflowmatching,whereeachsteprequiresrunninga
emphasizesthemiddletimesteps;theauthorspositthatathigh forwardpassonthetokenscorrespondingtoAτ (thekeysand
t
timesteps(lownoiselevels),themodelneedsonlytolearnthe values corresponding to o are cached). Table I summarizes
t
identity function, and at low timesteps (high noise levels), the thecomputationtimeforthisoperationwith3cameraimages.
model needs only to learn the mean of the data distribution. The operations were timed on an NVIDIA GeForce RTX
However, we hypothesize that the task of action prediction is 4090 consumer-grade GPU. For the mobile robot, inference
subtlydifferentfromhigh-resolutionimagesynthesis—while was done off-board over a Wi-Fi connection, adding a small
itmayberelativelyeasytopredictthemeanimageconditioned amount of network latency. Further optimizations, quantiza-
on a text label, predicting the mean action conditioned on a tion, and other improvements might further reduce inference
robot observation (i.e., learning E[A |o ]) is a much harder times.
t t
problem;thisisbecausetheobservationo isveryinformative Since the model generates an entire H-step action chunk
t
in that it should constrain the distribution of possible actions at once, we can execute up to H actions before we need to
much more than a text label constrains the distribution of run inference again. However, we may run inference more
possibleimages.Asaresult,wedesignedatimestepsampling often than that, as well as combine actions from different
distribution that emphasizes low timesteps (high noise levels); inference calls using various aggregation strategies. We tried
additionally, timesteps above a given threshold s are not temporal ensembling [57] early on and found that it hurt
sampled at all, since they are not needed so long as the policy performance, so we opted not to aggregate actions and
integrationstepδisgreaterthan1−s.Thedistributionisgiven instead execute action chunks open-loop. For the 20Hz UR5e
byp(τ)=Beta(s−τ;1.5,1)andisvisualizedinFigure14.We and Franka robots, we run inference every 0.8 seconds (after
s
use s=0.999 in our experiments, which allows for δ > 1 , executing 16 actions), and for all other robots, which run at
1000
or up to 1,000 integration steps. 50Hz, we run inference every 0.5 seconds (after executing 25
actions).
C. Non-VLM Baseline Architecture
modelpart inferencetime
Our baseline architecture π -small is not based on a VLM
0
imageencoders 14ms
backbone. Hence, we use it to evaluate the benefits of VLM-
observationforwardpass 32ms
pre-training. We design it to be sufficiently expressive to fit x10actionforwardpass(flow) 27ms
ourlargedatasetwhilestillprovidinggoodperformancewhen networklatency(ifoff-board) 13ms
trained from scratch. This model has about 470M parameters, totalon-boardinference 73ms
and differs from our main model in the following ways: (1) totaloff-boardinference 86ms
We use DistilBERT [42] to encode the language tokens of
TABLEI:InferencetimeofourmodelonanNVIDIAGeForce
the language command ℓ , since this model does not use a
t RTX 4090 GPU.
languagemodel backbone;(2) Theaction expertcross-attends
to the outputs of the observation encoder, akin to a traditional
encoder-decodertransformer[51],ratherthanourmainmodel E. Evaluation Details
which is more like a decoder-only mixture of experts [45]; For each task, we design a score rubric that measures
(3) The images are encoded with a smaller pre-trained ViT progress on the task, and use this for our quantitative results.

--- Page 17 ---
We describe this rubric for each task below: placed into the drawer, and one point for closing the drawer.
A. Evaluating the base model D. Mastering complex multi-stage tasks
Shirt folding: Shirt folding is recorded as either success or Laundry folding:Thistaskisscoredoutof4.Ourevaluation
failure. We begin each shirt folding eval by laying the shirt includes five items, three shirts of size M, L, and XL and two
flat on the table. Success is defined as having folded in the shorts of size 28 and 36. We perform two trials for each item,
sleeves and performed one half-fold along the length of the andtheitemslefttobeevaluatedstartrandomlycrumpledina
shirt. Our eval includes 4 small t-shirts and 1 medium t-shirt. laundrybin(whilepreviouslyevaluateditemsstartinafolded
We run 2 evals for each item for a maximum of 15000 steps stack). One point is given for picking an item out of the bin
or approximately 5 minutes each. andputtingitonthetable.Anotherpointisgivenforflattening
Bussing easy: This task is scored out of 7, where there are theshirtorshorts.Athirdpointisgrantedforfoldingtheshirt
7 different objects on the table, and 1 point is given for each or shorts. A final point is given for either placing the item in
correctly sorted object. the corner of the table (if it is the first item evaluated), or
Bussing hard: This task is scored out of 12, where there stacking it onto an existing stack of folded clothes. We run
are 12 different objects on the table, and 1 point is given for each eval for a maximum of 15000 steps or approximately 5
each correctly sorted object. This version of the task includes minutes.
particularly challenging settings, like a chopstick on top of a Mobile laundry: This evaluation follows the same protocol
piece of trash. as laundry folding. The three shirts are sized M, M, and XL,
Grocery bagging: This task is scored out of 7. For each 7 and the shorts are sized 32 and 31 W.
grocery items, a point is given for putting it in the bag. Table bussing: This task is scored out of 12, where there
Toast out of toaster: This task is scored out of 4. For each are 12 different objects on the table, and 1 point is given for
piece of toast, 1 point is given for picking it from the toaster each correctly sorted object. This version of the task includes
and another for putting it on the plate. particularly challenging settings, like a chopstick on top of a
B. Language instruction following. The policy is scored on piece of trash.
successfully repositioning each object and whether it follows Box building:Thistaskisscoredoutof5.Onepointisgiven
instructions. for successfully picking up the box to begin the task. One
Bussing: The robot has to follow the command to pick up point is given for folding the box in half, so the flaps can be
the correct object and place each of them into the correct closed.Onepointisgivenforclosingtherightflap.Onepoint
receptacle. The robot receives 12 objects in total and around is given for closing the left flap. The final point is given for
30 instructions in one episode. neatly centering the final product.
Table setting: The robot arranges all dishes, utensils, and Packingeggs:Thistaskisscoredoutof7.Onepointforeach
napkins and makes adjustments according to language speci- egg placed in the correct slot in the carton, and one point for
fication. The robot receives 7 objects in total and around 20 closing the lid.
instructions in one episode. Packing food: This task is scored out of 5. One point for
Grocerybagging:Therobotpicksupthecorrectitem(among picking up the plate of food, one point for each of 3 food
bag of coffee beans, bag of barley, bag of marshmallow, cat items placed in the to-go box, and one point for closing the
food, spaghetti, bag of seaweed, bag of almonds), and bags to-go box.
them into a paper bag. The robot receives 7 objects in total Dryer unloading: This task involves having the robot ap-
and around 14 instructions in one episode. proach a dyer with a laundry basket and unload the clothes
C. Learning new dexterous tasks into the basket. We score this eval out of five, where one
Stack bowls: This task is scored out of 3. One point for each point is given for properly approaching the dryer. Another for
oftwobowlsstackedinlargerbowls,andonefortheneatness placing the laundry basket on the stool. A third for opening
of the final product. thedryer.Afourthforputtingalltheclothesinthebasketand
Towel folding: This task is scored out of 3. One point for the a fifth point for closing the dryer. We eval with 3 shirts and
first half-fold of the towel, one point for the second half-fold 2 shorts that start in a random configuration inside the dryer.
of the towel, and one point for neatness of the final product.
Tupperware in microwave:Thistaskisscoredoutof4.One
point for opening the microwave, one point for picking up
the Tupperware, one point for putting the Tupperware in the
microwave, and one point for closing the microwave.
Paper towel replacement: This task is scored out of 4. One
point is given for grasping the old roll, and another point is
givenforremovingit.Then,onepointisgivenforgraspingthe
new paper towel roll, and the final point is given for placing
it on the dispenser.
Items in drawer: This task is scored out of 5. One point for
opening the drawer, one point for each of 3 items picked and