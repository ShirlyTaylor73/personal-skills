--- Page 1 ---
Learning Fine-Grained Bimanual Manipulation with
Low-Cost Hardware
Tony Z. Zhao1 Vikash Kumar3 Sergey Levine2 Chelsea Finn1
1 Stanford University 2 UC Berkeley 3 Meta
Fig. 1: ALOHA :ALow-costOpen-sourceHardwareSystemforBimanualTeleoperation.Thewholesystemcosts<$20kwithoff-the-shelf
robotsand3Dprintedcomponents.Left:Theuserteleoperatesbybackdrivingtheleaderrobots,withthefollowerrobotsmirroringthemotion.
Right: ALOHA is capable of precise, contact-rich, and dynamic tasks. We show examples of both teleoperated and learned skills.
Abstract—Finemanipulationtasks,suchasthreadingcableties off the table. Next, one of the right fingers approaches the
or slotting a battery, are notoriously difficult for robots because cup from below and pries the lid open. Each of these steps
they require precision, careful coordination of contact forces,
requires high precision, delicate hand-eye coordination, and
andclosed-loopvisualfeedback.Performingthesetaskstypically
rich contact. Millimeters of error would lead to task failure.
requireshigh-endrobots,accuratesensors,orcarefulcalibration,
which can be expensive and difficult to set up. Can learning Existing systems for fine manipulation use expensive robots
enable low-cost and imprecise hardware to perform these fine and high-end sensors for precise state estimation [29, 60, 32,
manipulation tasks? We present a low-cost system that performs 41].Inthiswork,weseektodevelopalow-costsystemforfine
end-to-end imitation learning directly from real demonstrations,
manipulation that is, in contrast, accessible and reproducible.
collected with a custom teleoperation interface. Imitation learn-
However, low-cost hardware is inevitably less precise than
ing, however, presents its own challenges, particularly in high-
precisiondomains:errorsinthepolicycancompoundovertime, high-endplatforms,makingthesensingandplanningchallenge
and human demonstrations can be non-stationary. To address more pronounced. One promising direction to resolve this is
thesechallenges,wedevelopasimpleyetnovelalgorithm,Action to incorporate learning into the system. Humans also do not
Chunking with Transformers (ACT), which learns a generative
have industrial-grade proprioception [71], and yet we are able
model over action sequences. ACT allows the robot to learn 6
to perform delicate tasks by learning from closed-loop visual
difficult tasks in the real world, such as opening a translucent
condiment cup and slotting a battery with 80-90% success, feedback and actively compensating for errors. In our system,
with only 10 minutes worth of demonstrations. Project website: we therefore train an end-to-end policy that directly maps
tonyzhaozh.github.io/aloha RGB images from commodity web cameras to the actions.
This pixel-to-action formulation is particularly suitable for
I. INTRODUCTION
fine manipulation, because fine manipulation often involves
Fine manipulation tasks involve precise, closed-loop feed- objectswithcomplexphysicalproperties,suchthatlearningthe
back and require high degrees of hand-eye coordination to manipulation policy is much simpler than modeling the whole
adjust and re-plan in response to changes in the environment. environment. Take the condiment cup example: modeling the
Examples of such manipulation tasks include opening the lid contact when nudging the cup, and also the deformation when
ofacondimentcuporslottingabattery,whichinvolvedelicate pryingopenthelidinvolvescomplexphysicsonalargenumber
operations such as pinching, prying, and tearing rather than of degrees of freedom. Designing a model accurate enough for
broad-strokemotionssuchaspickingandplacing.Takeopening planning would require significant research and task specific
the lid of a condiment cup in Figure 1 as an example, where engineering efforts. In contrast, the policy of nudging and
the cup is initialized upright on the table: the right gripper opening the cup is much simpler, since a closed-loop policy
needs to first tip it over, and nudge it into the opened left can react to different positions of the cup and lid rather than
gripper. Then the left gripper closes gently and lifts the cup precisely anticipating how it will move in advance.
3202
rpA
32
]OR.sc[
1v50731.4032:viXra

--- Page 2 ---
Training an end-to-end policy, however, presents its own II. RELATEDWORK
challenges. The performance of the policy depends heavily
on the training data distribution, and in the case of fine Imitationlearningforroboticmanipulation.Imitationlearn-
manipulation, high-quality human demonstrations can provide ing allows a robot to directly learn from experts. Behavioral
tremendous value by allowing the system to learn from human cloning (BC) [44] is one of the simplest imitation learning
dexterity. We thus build a low-cost yet dexterous teleoperation algorithms, casting imitation as supervised learning from
system for data collection, and a novel imitation learning observations to actions. Many works have then sought to
algorithm that learns effectively from the demonstrations. We improveBC,forexamplebyincorporatinghistorywithvarious
overview each component in the following two paragraphs. architectures[39,49,26,7],usingadifferenttrainingobjective
Teleoperation system. We devise a teleoperation setup with [17, 42], and including regularization [46]. Other works
two sets of low-cost, off-the-shelf robot arms. They are emphasize the multi-task or few-shot aspect of imitation
approximately scaled versions of each other, and we use joint- learning [14, 25, 11], leveraging language [51, 52, 26, 7], or
space mapping for teleoperation. We augment this setup with exploiting the specific task structure [43, 68, 28, 52]. Scaling
3D printed components for easier backdriving, leading to a these imitation learning algorithms with more data has led
highly capable teleoperation system within a $20k budget. We to impressive systems that can generalize to new objects,
showcase its capabilities in Figure 1, including teleoperation instructions, or scenes [15, 26, 7, 32]. In this work, we focus
of precise tasks such as threading a zip tie, dynamic tasks such on building an imitation learning system that is low-cost yet
as juggling a ping pong ball, and contact-rich tasks such as capable of performing delicate, fine manipulation tasks. We
assembling the chain in the NIST board #2 [4]. tackle this from both hardware and software, by building a
Imitationlearningalgorithm.Tasksthatrequireprecisionand high-performance teleoperation system, and a novel imitation
visual feedback present a significant challenge for imitation learning algorithm that drastically improves previous methods
learning, even with high-quality demonstrations. Small errors on fine manipulation tasks.
in the predicted action can incur large differences in the state, Addressingcompoundingerrors.AmajorshortcomingofBC
exacerbating the “compounding error” problem of imitation is compounding errors, where errors from previous timesteps
learning [47, 64, 29]. To tackle this, we take inspiration from accumulate and cause the robot to drift off of its training
action chunking, a concept in psychology that describes how distribution, leading to hard-to-recover states [47, 64]. This
sequences of actions are grouped together as a chunk, and problem is particularly prominent in the fine manipulation
executed as one unit [35]. In our case, the policy predicts the setting [29]. One way to mitigate compounding errors is to
target joint positions for the next k timesteps, rather than just allow additional on-policy interactions and expert corrections,
onestepatatime.Thisreducestheeffectivehorizonofthetask such as DAgger [47] and its variants [30, 40, 24]. However,
by k-fold, mitigating compounding errors. Predicting action expert annotation can be time-consuming and unnatural with
sequences also helps tackle temporally correlated confounders a teleoperation interface [29]. One could also inject noise at
[61], such as pauses in demonstrations that are hard to model demonstrationcollectiontimetoobtaindatasetswithcorrective
with Markovian single-step policies. To further improve the behavior [36], but for fine manipulation, such noise injection
smoothness of the policy, we propose temporal ensembling, can directly lead to task failure, reducing the dexterity of
which queries the policy more frequently and averages across teleoperation system. To circumvent these issues, previous
the overlapping action chunks. We implement action chunking works generate synthetic correction data in an offline manner
policy with Transformers [65], an architecture designed for [16, 29, 70]. While they are limited to settings where low-
sequence modeling, and train it as a conditional VAE (CVAE) dimensional states are available, or a specific type of task like
[55, 33] to capture the variability in human data. We name our grasping. Due to these limitations, we need to address the
method Action Chunking with Transformers (ACT), and find compounding error problem from a different angle, compatible
that it significantly outperforms previous imitation learning with high-dimensional visual observations. We propose to
algorithms on a range of simulated and real-world fine reduce the effective horizon of tasks through action chunking,
manipulation tasks. i.e., predicting an action sequence instead of a single action,
The key contribution of this paper is a low-cost system for andthenensembleacrossoverlappingactionchunkstoproduce
learning fine manipulation, comprising a teleoperation system trajectories that are both accurate and smooth.
and a novel imitation learning algorithm. The teleoperation Bimanual manipulation. Bimanual manipulation has a long
system, despite its low cost, enables tasks with high precision historyinrobotics,andhasgainedpopularitywiththelowering
and rich contacts. The imitation learning algorithm, Action of hardware costs. Early works tackle bimanual manipulation
Chunking with Transformers (ACT), is capable of learning pre- from a classical control perspective, with known environment
cise, close-loop behavior and drastically outperforms previous dynamics [54, 48], but designing such models can be time-
methods. The synergy between these two parts allows learning consuming, and they may not be accurate for objects with
of 6 fine manipulation skills directly in the real-world, such as complex physical properties. More recently, learning has been
openingatranslucentcondimentcupandslottingabatterywith incorporated into bimanual systems, such as reinforcement
80-90% success, from only 10 minutes or 50 demonstration learning [9, 10], imitating human demonstrations [34, 37, 59,
trajectories. 67, 32], or learning to predict key points that chain together

--- Page 3 ---
top camera
wrist camera wrist camera
see-through gripper
adjustable velcro
front camera
50cm
grip tape
mc06
ViperX 6dof Arm (follower)
#Dofs 6+gripper
Reach 750mm
Span 1500mm
Repeatability 1mm
Accuracy 5-8mm
Working Payload 750g
red: bimanual workspace
Fig. 3: Left: Camera viewpoints of the front, top, and two wrist cameras, together with an illustration of the bimanual workspace of ALOHA.
Middle: Detailed view of the “handle and scissor” mechanism and custom grippers. Right: Technical spec of the ViperX 6dof robot [1].
motor primitives [20, 19, 50]. Some of the works also focus whenperformingdelicateoperations,androbustgripevenwith
on fine-grained manipulation tasks such as knot untying, cloth thin plastic films.
flattening, or even threading a needle [19, 18, 31], while using We then seek to design a teleoperation system that is
robots that are considerably more expensive, e.g. the da Vinci maximally user-friendly around the ViperX robot. Instead
surgical robot or ABB YuMi. Our work turns to low-cost of mapping the hand pose captured by a VR controller or
hardware, e.g. arms that cost around $5k each, and seeks to camera to the end-effector pose of the robot, i.e. task-space
enable them to perform high-precision, closed-loop tasks. Our mapping, we use direct joint-space mapping from a smaller
teleoperation setup is most similar to Kim et al. [32], which robot, WidowX, manufactured by the same company and costs
also uses joint-space mapping between the leader and follower $3300 [2]. The user teleoperates by backdriving the smaller
robots. Unlike this previous system, we do not make use of WidowX(“theleader”),whosejointsaresynchronizedwiththe
special encoders, sensors, or machined components. We build larger ViperX (“the follower”). When developing the setup, we
our system with only off-the-shelf robots and a handful of 3D noticed a few benefits of using joint-space mapping compared
printed parts, allowing non-experts to assemble it in less than to task-space. (1) Fine manipulation often requires operating
2 hours. near singularities of the robot, which in our case has 6 degrees
offreedomandnoredundancy.Off-the-shelfinversekinematics
III. ALOHA:ALOW-COSTOPEN-SOURCEHARDWARE
(IK) fails frequently in this setting. Joint space mapping, on
SYSTEMFORBIMANUALTELEOPERATION
the other hand, guarantees high-bandwidth control within the
We seek to develop an accessible and high-performance jointlimits,whilealsorequiringlesscomputationandreducing
teleoperation system for fine manipulation. We summarize our latency. (2) The weight of the leader robot prevents the user
design considerations into the following 5 principles. from moving too fast, and also dampens small vibrations.
1) Low-cost: The entire system should be within budget for We notice better performance on precise tasks with joint-
most robotic labs, comparable to a single industrial arm. space mapping rather than holding a VR controller. To further
2) Versatile: It can be applied to a wide range of fine improve the teleoperation experience, we design a 3D-printed
manipulation tasks with real-world objects. “handle and scissor” mechanism that can be retrofitted to the
3) User-friendly: The system should be intuitive, reliable, leader robot (Fig 3). It reduces the force required from the
and easy to use. operator to backdrive the motor, and allows for continuous
4) Repairable: The setup can be easily repaired by re- control of the gripper, instead of binary opening or closing.
searchers, when it inevitably breaks. We also design a rubber band load balancing mechanism that
5) Easy-to-build:Itcanbequicklyassembledbyresearchers, partiallycounteractsthegravityontheleaderside.Itreducesthe
with easy-to-source materials. effortneededfromtheoperatorandmakeslongerteleoperation
When choosing the robot to use, principles 1, 4, and 5 lead sessions (e.g. >30 minutes) possible. We include more details
us to build a bimanual parallel-jaw grippers setup with two about the setup in the project website.
ViperX6-DoFrobotarms[1,66].Wedonotemploydexterous The rest of the setup includes a robot cage with 20×20mm
handsduetopriceandmaintenanceconsiderations.TheViperX aluminumextrusions,reinforcedbycrossingsteelcables.There
arm used has a working payload of 750g and 1.5m span, with is a total of four Logitech C922x webcams, each streaming
an accuracy of 5-8mm. The robot is modular and simple to 480×640 RGB images. Two of the webcams are mounted on
repair: in the case of motor failure, the low-cost Dynamixel the wrist of the follower robots, allowing for a close-up view
motors can be easily replaced. The robot can be purchased ofthegrippers.Theremainingtwocamerasaremountedonthe
off-the-shelf for around $5600. The OEM fingers, however, front and at the top respectively (Fig 3). Both the teleoperation
are not versatile enough to handle fine manipulation tasks. We and data recording happen at 50Hz.
thus design our own 3D printed “see-through” fingers and fit Withthedesignconsiderationsabove,webuildthebimanual
it with gripping tape (Fig 3). This allows for good visibility teleoperation setup ALOHA within a 20k USD budget, compa-

--- Page 4 ---
action sequence
…
1
2
transformer transformer transformer
encoder encoder decoder
3
… 4 … …
joints action sequence + PosEmb 480X640X3 CNN cam 1 cam 4 joints position embeddings (fixed)
+PosEmb
0 1 2 3 4 5 6
t=0
t=4
Action Chunking + Temporal Ensemble
t=0
t=1
t=2
t=3
…
action sequence
…
1
… … …
style variable
2
transformer transformer transformer
encoder encoder decoder
3
… 4 … …
… …
joints action sequence + PosEmb 480X640X3 CNN cam 1 cam 4 joints position embeddings (fixed)
[CLS] +PosEmb
Fig. 4: Architecture of Action Chunking withTransformers (ACT). We train ACT as a Conditional VAE (CVAE), which has anencoder and a
decoder.Left:TheencoderoftheCVAEcompressesactionsequenceandjointobservationintoz,thestylevariable.Theencoderisdiscarded
at test time. Right: The decoder or policy of ACT synthesizes images from multiple viewpoints, joint positions, and z with a transformer
encoder, and predicts a sequence of actions with a transformer decoder. z is simply set to the mean of the prior (i.e. zero) at test time.
Action Chunking
0 1 2 3 4 5 76
t=0
t=4
Action Chunking + Temporal Ensemble
x [0.5, 0.3, 0.2, 0.1] =
t=0
t=1
t=2
t=3
…
… … …
style variable
… …
[CLS]
Action Chunking To train ACT on a new task, we first collect human
7 demonstrations using ALOHA. We record the joint positions of
the leader robots (i.e. input from the human operator) and use
them as actions. It is important to use the leader joint positions
instead of the follower’s, because the amount of force applied
x [0.5, 0.3, 0.2, 0.1] = is implicitly defined by the difference between them, through
thelow-levelPIDcontroller.Theobservationsarecomposedof
thecurrentjointpositionsoffollowerrobotsandtheimagefeed
from 4 cameras. Next, we train ACT to predictthe sequence of
future actions given the current observations. An action here
corresponds to the target joint positions for both arms in the
Fig. 5: We employ both Action Chunking and Temporal Ensembling next time step. Intuitively, ACT tries to imitate what a human
whenapplyingactions,insteadofinterleavingobservingandexecuting.
operator would do in the following time steps given current
observations. These target joint positions are then tracked by
rable to a single research arm such as Franka Emika Panda.
the low-level, high-frequency PID controller inside Dynamixel
ALOHA enables the teleoperation of:
motors. At test time, we load the policy that achieves the
• Precise tasks such as threading zipcable ties, picking credit
lowest validation loss and roll it out in the environment. The
cards out of wallets, and opening or closing ziploc bags.
main challenge that arises is compounding errors, where errors
• Contact-rich tasks such as inserting 288-pin RAM into
from previous actions lead to states that are outside of training
a computer motherboard, turning pages of a book, and
distribution.
assembling the chains and belts in the NIST board #2 [4]
• Dynamic tasks such as juggling a ping pong ball with a
A. Action Chunking and Temporal Ensemble
real ping pong paddle, balancing the ball without it falling
off, and swinging open plastic bags in the air. Tocombatthecompoundingerrorsofimitationlearningina
Skills such as threading a zip tie, inserting RAM, and juggling way that is compatible with pixel-to-action policies (Figure II),
ping pong ball, to our knowledge, are not available for existing we seek to reduce the effective horizon of long trajectories
teleoperationsystemswith5-10xthebudget[21,5].Weinclude collectedathighfrequency.Weareinspiredbyactionchunking,
a more detailed price & capability comparison in Appendix A, a neuroscience concept where individual actions are grouped
as well as more skills that ALOHA is capable of in Figure 9. together and executed as one unit, making them more efficient
To make ALOHA more accessible, we open-source all software to store and execute [35]. Intuitively, a chunk of actions could
and hardware with a detailed tutorial covering 3D printing, correspond to grasping a corner of the candy wrapper or
assembling the frame to software installations. You can find inserting a battery into the slot. In our implementation, we
the tutorial on the project website. fix the chunk size to be k: every k steps, the agent receives
an observation, generates the next k actions, and executes the
IV. ACTIONCHUNKINGWITHTRANSFORMERS actions in sequence (Figure 5). This implies a k-fold reduction
As we will see in Section V, existing imitation learning in the effective horizon of the task. Concretely, the policy
algorithms perform poorly on fine-grained tasks that require models π (a |s ) instead of π (a |s ). Chunking can also
θ t:t+k t θ t t
high-frequency control and closed-loop feedback. We therefore help model non-Markovian behavior in human demonstrations.
develop a novel algorithm, Action Chunking with Transformers Specifically,asingle-steppolicywouldstrugglewithtemporally
(ACT), to leverage the data collected by ALOHA. We first correlated confounders, such as pauses in the middle of a
summarize the pipeline of training ACT, then dive into each demonstration [61], since the behavior not only depends on
of the design choices. the state, but also the timestep. Action chunking can mitigate

--- Page 5 ---
Algorithm 1 ACT Training action chunking policy as a generative model. Specifically, we
1: Given: Demo dataset D, chunk size k, weight β. trainthepolicyasaconditionalvariationalautoencoder(CVAE)
2: Let a t , o t represent action and observation at timestep t, o¯ t [55], to generate an action sequence conditioned on current
represent o t without image observations. observations.TheCVAEhastwocomponents:aCVAEencoder
3: Initialize encoder q φ (z|a t:t+k ,o¯ t ) and a CVAE decoder, illustrated on the left and right side of
4: Initialize decoder π θ (aˆ t:t+k |o t ,z)
5: for iteration n=1,2,... do Figure 4 respectively. The CVAE encoder only serves to train
6: Sample o t , a t:t+k from D the CVAE decoder (the policy) and is discarded at test time.
7: Sample z from q φ (z|a t:t+k ,o¯ t ) Specifically, the CVAE encoder predicts the mean and variance
8: Predict aˆ t:t+k from π θ (aˆ t:t+k |o t ,z) of the style variable z’s distribution, which is parameterized as
9: L reconst =MSE(aˆ t:t+k ,a t:t+k ) a diagonal Gaussian, given the current observation and action
10: L reg =D KL (q φ (z|a t:t+k ,o¯ t )(cid:107)N(0,I))
11: Update θ, φ with ADAM and L=L reconst +βL reg sequence as inputs. For faster training in practice, we leave out
theimageobservationsandonlyconditionontheproprioceptive
observation and the action sequence. The CVAE decoder, i.e.
Algorithm 2 ACT Inference
the policy, conditions on both z and the current observations
1: Given: trained π θ , episode length T, weight m. (images + joint positions) to predict the action sequence. At
2: Initialize FIFO buffers B[0 : T], where B[t] stores actions test time, we set z to be the mean of the prior distribution i.e.
predicted for timestep t.
zerotodeterministicallydecode.Thewholemodelistrainedto
3: for timestep t=1,2,...T do
4: Predict aˆ t:t+k with π θ (aˆ t:t+k |o t ,z) where z=0 maximiz (cid:80) ethelog-likelihoodofdemonstrationactionchunks,i.e.
5 6 : : A O d b d tai aˆ n t: c t+ ur k re t n o t b s u te f p fer a s ct B io [ n t s : A t+ t = k] B re [t s ] pectively m ob i j n e θ ct − ivew s h t, i a c t h :t+ h k a ∈ s D tw l o og te π r θ m ( s a : t: a t+ re k c |s o t n ) s , tr w u i c t t h io t n he lo s s t s an a d n a d rd a V te A rm E
(cid:80) (cid:80)
7: Apply a t = i w i A t [i]/ i w i , with w i =exp(−m∗i) thatregularizestheencodertoaGaussianprior.Following[23],
weweightthesecondtermwithahyperparameterβ.Intuitively,
higher β will result in less information transmitted in z [62].
this issue when the confounder is within a chunk, without Overall, we found the CVAE objective to be essential in
introducing the causal confusion issue for history-conditioned learning precise tasks from human demonstrations. We include
policies [12]. a more detailed discussion in Subsection VI-B.
A naïve implementation of action chunking can be sub-
C. Implementing ACT
optimal: a new environment observation is incorporated
abruptly every k steps and can result in jerky robot motion. We implement the CVAE encoder and decoder with trans-
To improve smoothness and avoid discrete switching between formers, as transformers are designed for both synthesizing in-
executingandobserving,wequerythepolicyateverytimestep. formationacrossasequenceandgeneratingnewsequences.The
This makes different action chunks overlap with each other, CVAE encoder is implemented with a BERT-like transformer
and at a given timestep there will be more than one predicted encoder [13]. The inputs to the encoder are the current joint
action. We illustrate this in Figure 5 and propose a temporal positions and the target action sequence of length k from the
ensemble tocombinethese predictions.Ourtemporalensemble demonstration dataset, prepended by a learned “[CLS]” token
performs a weighted average over these predictions with an similartoBERT.Thisformsak+2lengthinput(Figure4left).
exponential weighting scheme w =exp(−m∗i), where w Afterpassingthroughthetransformer,thefeaturecorresponding
i 0
is the weight for the oldest action. The speed for incorporating to“[CLS]”isusedtopredictthemeanandvarianceofthe“style
new observation is governed by m, where a smaller m means variable” z, which is then used as input to the decoder. The
faster incorporation. We note that unlike typical smoothing, CVAE decoder (i.e. the policy) takes the current observations
where the current action is aggregated with actions in adjacent and z as the input, and predicts the next k actions (Figure 4
timesteps, which leads to bias, we aggregate actions predicted right). We use ResNet image encoders, a transformer encoder,
for the same timestep. This procedure also incurs no additional and a transformer decoder to implement the CVAE decoder.
trainingcost,onlyextrainference-timecomputation.Inpractice, Intuitively, the transformer encoder synthesizes information
we find both action chunking and temporal ensembling to be from different camera viewpoints, the joint positions, and the
important for the success of ACT, which produces precise and stylevariable,andthetransformerdecodergeneratesacoherent
smooth motion. We discuss these components in more detail actionsequence.Theobservationincludes4RGBimages,each
in the ablation studies in Subsection VI-A. at 480×640 resolution, and joint positions for two robot arms
(7+7=14 DoF in total). The action space is the absolute joint
B. Modeling human data
positions for two robots, a 14-dimensional vector. Thus with
Another challenge that arises is learning from noisy human action chunking, the policy outputs a k × 14 tensor given
demonstrations. Given the same observation, a human can use the current observation. The policy first process the images
different trajectories to solve the task. Humans will also be with ResNet18 backbones [22], which convert 480×640×3
more stochastic in regions where precision matters less [38]. RGB images into 15×20×512 feature maps. We then flatten
Thus, it is important for the policy to focus on regions where along the spatial dimension to obtain a sequence of 300×512.
high precision matters. We tackle this problem by training our To preserve the spatial information, we add a 2D sinusoidal

--- Page 6 ---
position embedding to the feature sequence [8]. Repeating this table, followed by the right gripper pinching the tail of the
for all 4 images gives a feature sequence of 1200×512 in tie in mid-air. Then, both arms coordinate to insert one end
dimension. We then append two more features: the current of the velcro tie into the other in mid-air. The loop measures
joint positions and the “style variable” z. They are projected 3mm x 25mm, while the velcro tie measures 2mm x 10-25mm
from their original dimensions to 512 through linear layers depending on the position. For this task to be successful, the
respectively. Thus, the input to the transformer encoder is robot must use visual feedback to correct for perturbations
1202×512.Thetransformerdecoderconditionsontheencoder with each grasp, as even a few millimeters of error during the
output through cross-attention, where the input sequence is a first grasp will compound in the second grasp mid-air, giving
fixed position embedding, with dimensions k×512, and the more than a 10mm deviation in the insertion phase. For Prep
keys and values are coming from the encoder. This gives the Tape, the goal is to hang a small segment of the tape on the
transformer decoder an output dimension of k×512, which is edge of a cardboard box. The right gripper first grasps the tape
then down-projected with an MLP into k×14, corresponding and cuts it with the tape dispenser’s blade, and then hands
to the predicted target joint positions for the next k steps. We the tape segment to the left gripper mid-air. Next, both arms
use L1 loss for reconstruction instead of the more common approach the box, the left arm gently lays the tape segment
L2 loss: we noted that L1 loss leads to more precise modeling on the box surface, and the right fingers push down on the
of the action sequence. We also noted degraded performance tape to prevent slipping, followed by the left arm opening its
when using delta joint positions as actions instead of target gripper to release the tape. Similar to Thread Velcro, this task
joint positions. We include a detailed architecture diagram in requires multiple steps of delicate coordination between the
Appendix C. two arms. For Put On Shoe, the goal is to put the shoe on a
We summarize the training and inference of ACT in fixedmanniquinfoot,andsecureitwiththeshoe’svelcrostrap.
Algorithms 1 and 2. The model has around 80M parameters, The arms would first need to grasp the tongue and collar of
and we train from scratch for each task. The training takes the shoe respectively, lift it up and approach the foot. Putting
around 5 hours on a single 11G RTX 2080 Ti GPU, and the the shoe on is challenging because of the tight fitting: the arms
inference time is around 0.01 seconds on the same machine. would need to coordinate carefully to nudge the foot in, and
both grasps need to be robust enough to counteract the friction
V. EXPERIMENTS
between the sock and shoe. Then, the left arm goes around to
We present experiments to evaluate ACT’s performance on thebottomoftheshoetosupportitfromdropping,followedby
fine manipulation tasks. For ease of reproducibility, we build the right arm flipping the velcro strap and pressing it against
two simulated fine manipulation tasks in MuJoCo [63], in the shoe to secure. The task is only considered successful if
addition to 6 real-world tasks with ALOHA. We provide videos the shoe clings to the foot after both arms releases. For the
for each task on the project website. simulated task Transfer Cube, the right arm needs to first pick
up the red cube lying on the table, then place it inside the
A. Tasks
gripper of the other arm. Due to the small clearance between
All 8 tasks require fine-grained, bimanual manipulation, and the cube and the left gripper (around 1cm), small errors could
are illustrated in Figure 6. For Slide Ziploc, the right gripper result in collisions and task failure. For the simulated task
needs to accurately grasp the slider of the ziploc bag and open Bimanual Insertion, the left and right arms need to pick up
it, with the left gripper securing the body of the bag. For Slot the socket and peg respectively, and then insert in mid-air so
Battery, the right gripper needs to first place the battery into the peg touches the “pins” inside the socket. The clearance is
the slot of the remote controller, then using the tip of fingers around 5mm in the insertion phase. For all 8 tasks, the initial
to delicately push in the edge of the battery, until it is fully placement of the objects is either varied randomly along the
inserted. Because the spring inside the battery slot causes the 15cm white reference line (real-world tasks), or uniformly in
remote controller to move in the opposite direction during 2D regions (simulated tasks). We provide illustrations of both
insertion, the left gripper pushes down on the remote to keep the initial positions and the subtasks in Figure 6 and 7. Our
it in place. For Open Cup, the goal is to open the lid of a evaluation will additionally report the performance for each of
small condiment cup. Because of the cup’s small size, the these subtasks.
grippers cannot grasp the body of the cup by just approaching In addition to the delicate bimanual control required to
it from the side. Therefore we leverage both grippers: the right solve these tasks, the objects we use also present a significant
fingers first lightly tap near the edge of the cup to tip it over, perception challenge. For example, the ziploc bag is largely
and then nudge it into the open left gripper. This nudging transparent, with a thin blue sealing line. Both the wrinkles
step requires high precision and closing the loop on visual on the bag and the reflective candy wrappers inside can vary
perception. The left gripper then closes gently and lifts the cup during the randomization, and distract the perception system.
off the table, followed by the right finger prying open the lid, Other transparent or translucent objects include the tape and
which also requires precision to not miss the lid or damage both the lid and body of the condiment cup, making them
the cup. The goal of Thread Velcro is to insert one end of hardtoperceivepreciselyandill-suitedfordepthcameras.The
a velcro cable tie into the small loop attached to other end. blacktabletopalsocreatesalow-contrastagainstmanyobjects
The left gripper needs to first pick up the velcro tie from the of interest, such as the black velcro cable tie and the black

--- Page 7 ---
Real-World Task Definitions
init. #1 #2 #3
Slide Ziploc: Open the ziploc bag that is standing upright on the table. The bag is randomized along the 15cm white line. It is dropped from ~5cm
above the table to randomize the deformation, which affects the height and appearance of the bag. The left arm first grasps the bag body (Subtask#1
Grasp) followed by the right arm pinching the slider (Subtask #2 Pinch). Then the right arm moves right to unzip the bag (Subtask #3 Open).
init. #1 #2 #3
Slot Battery: Insert the battery into the remote controller. The controller is randomized along the 15cm white line. The battery is initialized in
roughly the same position with different rotations. The right arm first grasps the battery (Subtask#1 Grasp) then places it into the slot (Subtask#2
Place). The left arm presses onto the remote to prevent it from sliding, while the right arm pushes in the battery (Subtask#3 Insert).
init. #1 #2 #3
Open Cup: Pick up and open the lid of a translucent condiment cup. The cup is randomized along the 15cm white line. Both arms approach the cup,
and the right gripper gently tips over the cup (Subtask#1 Tip Over) and pushes it into the gripper of the left arm. The left arm then gently closes its
gripper and lifts the cup off the table (Subtask#2 Grasp). Next, the right gripper approaches the cup lid from below and prys open the lid.
init. #1 #2 #3
Thread Velcro: Pick up the velcro cable tie and insert one end into the small loop on the other end. The velcro tie is randomized along the 15cm
white line. The left arm first picks up the velcro tie by pinching near the plastic loop (Subtask#1 Lift). The right arm grasps the tail of the velcro tie
mid-air (Subtask#2 Grasp). Next, both arms coordinate to deform the velcro tie and insert one end of it into the plastic loop on the other end.
init. #1 #2 #3 #4
Prep Tape: Hang a short segment of tape on the edge of the box. The tape dispenser is randomized along the 15cm white line. First, the right gripper
grasps the tape from the side (Subtask#1 Grasp). It then lifts the tape and pulls to unroll it, followed by cutting it with the dispenser blade
(Subtask#2 Cut). Next, the right gripper hands the tape segment to the left gripper in mid-air (Subtask#3 Handover), and both arms move toward the
corner of the stationery cardboard box. The left arm then lays the tape segment flat on the surface of the box while the right gripper pushes down on
the tape to prevent slipping. The left arm then opens its gripper to release the tape (Subtask#4 Hang).
init. #1 #2 #3 #4
Put On Shoe: Put a velcro-strap shoe on a fixed manniquin foot. The shoe pose is randomized along the 15cm white line. First, both left and right
grippers pick up the shoe (Subtask#1 Lift). Then both arms coordinate to put it on, with the heel touching the heel counter (Subtask#2 Insert). Next,
the left arm moves to support the shoe (Subtask#3 Support), followed by the right arm securing the velcro strap (Subtask#4 Secure).
Fig. 6: Real-World Task Definitions. For each of the 6 real-world tasks, we illustrate the initializations and the subtasks.
init. #1 #2 #3 #4
Unwrap Candy Expose the candy by untwisting the wrapper. The candy is randomized along the 15cm white line. The right arm first lifts the candy
by pinching one side of the wrapper (Subtask#1 Lift). Then both arms coordinate to let the left gripper pinch the other end of the wrapper mid-air
(Subtask#2 Hold). Next, both arms pull to untwist the candy wrapper (Subtask#2 Untwist). Finally, the left arm holds the candy, while the right arm
pinches the wrapper to peel it open.

--- Page 8 ---
20cm
Left: Cube Transfer. Transfer the red cube to the other arm. The right arm touches (#1) and grasps (#2) the red cube, then hands it to the left arm.
Right: Bimanual Insertion. Insert the red peg into the blue socket. Both arms grasp (#1), let socket and peg make contact (#2) and insertion.
mc02
10cm
20cm
10cm
mc02
rand. region rand. regions
init. #1 #2 #3 init. #1 #2 #3
Fig. 7: Simulated Task Definitions. For each of the 2 simulated tasks, we illustrate the initializations and the subtasks.
CubeTransfer(sim) BimanualInsertion(sim) SlideZiploc(real) SlotBattery(real)
Touched Lifted Transfer Grasp Contact Insert Grasp Pinch Open Grasp Place Insert
BC-ConvMLP 34|3 17|1 1|0 5|0 1|0 1|0 0 0 0 0 0 0
BeT 60|16 51|13 27|1 21|0 4|0 3|0 8 0 0 4 0 0
RT-1 44|4 33|2 2|0 2|0 0|0 1|0 4 0 0 4 0 0
VINN 13|17 9|11 3|0 6|0 1|0 1|0 28 0 0 20 0 0
ACT(Ours) 97|82 90|60 86|50 93|76 90|66 32|20 92 96 88 100 100 96
TABLE I: Success rate (%) for 2 simulated and 2 real-world tasks, comparing our method with 4 baselines. For the two simulated tasks, we
report [training with scripted data | training with human data], with 3 seeds and 50 policy evaluations each. For the real-world tasks, we
report training with human data, with 1 seed and 25 evaluations. Overall, ACT significantly outperforms previous methods.
OpenCup(real) ThreadVelcro(real) PrepTape(real) PutOnShoe(real)
TipOver Grasp OpenLid Lift Grasp Insert Grasp Cut Handover Hang Lift Insert Support Secure
BeT 12 0 0 24 0 0 8 0 0 0 12 0 0 0
ACT(Ours) 100 96 84 92 40 20 96 92 72 64 100 92 92 92
TABLE II: Success rate (%) for the remaining 3 real-world tasks. We only compare with the best performing baseline BeT.
tape dispenser. Especially from the top view, it is challenging the handover, and the left gripper should always move to a
to localize the velcro tie because of the small projected area. position that can grasp the tape, instead of trying to memorize
where exactly the handover happens, which can vary across
B. Data Collection demonstrations.
For all 6 real-world tasks, we collect demonstrations using
C. Experiment Results
ALOHA teleoperation. Each episode takes 8-14 seconds for the
humanoperatortoperformdependingonthecomplexityofthe WecompareACTwithfourpriorimitationlearningmethods.
task, which translates to 400-700 time steps given the control BC-ConvMLP is the simplest yet most widely used base-
frequency of 50Hz. We record 50 demonstrations for each task, line [69, 26], which processes the current image observations
except for Thread Velcro which has 100. The total amount for with a convolutional network, whose output features are
demonstrations is thus around 10-20 minutes of data for each concatenated with the joint positions to predict the action.
task, and 30-60 minutes in wall-clock time because of resets BeT [49] also leverages Transformers as the architecture, but
and teleoperator mistakes. For the two simulated tasks, we withkeydifferences:(1)noactionchunking:themodelpredicts
collect two types of demonstrations: one type with a scripted one action given the history of observations; and (2) the image
policy and one with human demonstrations. To teleoperate in observations are pre-processed by a separately trained frozen
simulation, we use the “leader robots” of ALOHA to control visual encoder. That is, the perception and control networks
the simulated robot, with the operator looking at the real-time are not jointly optimized. RT-1 [7] is another Transformer-
renderings of the environment on the monitor. In both cases, based architecture that predicts one action from a fixed-length
we record 50 successful demonstrations. history of past observations. Both BeT and RT-1 discretize
We emphasize that all human demonstrations are inherently the action space: the output is a categorical distribution over
stochastic, even though a single person collects all of the discretebins,butwithanaddedcontinuousoffset fromthebin-
demonstrations. Take the mid-air hand handover of the tape center in the case of BeT. Our method, ACT, instead directly
segment as an example: the exact position of the handover predictscontinuousactions,motivatedbytheprecisionrequired
is different across each episode. The human has no visual or in fine manipulation. Lastly, VINN [42] is a non-parametric
haptic reference to perform it in the same position. Thus to method that assumes access to the demonstrations at test time.
successfully perform the task, the policy will need to learn that Given a new observation, it retrieves the k observations with
the two grippers should never collide with each other during the most similar visual features, and returns an action using

--- Page 9 ---
weighted k-nearest-neighbors. The visual feature extractor is ablateeachofthesecomponents,togetherwithauserstudythat
a pretrained ResNet finetuned on demonstration data with highlights the necessity of high-frequency control in ALOHA.
unsupervised learning. We carefully tune the hyperparameters We report results across a total of four settings: two simulated
of these four prior methods using cube transfer. Details of the tasks with scripted or human demonstration.
hyperparameters are provided in Appendix D.
A. Action Chunking and Temporal Ensembling
As a detailed comparison with prior methods, we report the
average success rate in Table I for two simulated and two real In Subsection V-C, we observed that ACT significantly
tasks. For simulated tasks, we average performance across 3 outperforms previous methods that only predict single-step
random seeds with 50 trials each. We report the success rate actions, with the hypothesis that action chunking is the key
on both scripted data (left of separation bar) and human data design choice. Since k dictates how long the sequence in each
(right of separation bar). For real-world tasks, we run one seed “chunk” is, we can analyze this hypothesis by varying k. k =1
and evaluate with 25 trials. ACT achieves the highest success corresponds to no action chunking, and k =episode_length
rate compared to all prior methods, outperforming the second corresponds to fully open-loop control, where the robot
best algorithm by a large margin on each task. For the two outputs the entire episode’s action sequence based on the
simulated tasks with scripted or human data, ACT outperforms first observation. We disable temporal ensembling in these
the best previous method in success rate by 59%, 49%, 29%, experimentstoonlymeasuretheeffectofchunking,andtrained
and 20%. While previous methods are able to make progress separatepoliciesforeachk.InFigure8(a),weplotthesuccess
in the first two subtasks, the final success rate remains low, rate averaged across 4 settings, corresponding to 2 simulated
below 30%. For the two real-world tasks Slide Ziploc and tasks with either human or scripted data, with the blue line
Slot Battery, ACT achieves 88% and 96% final success rates representing ACT without the temporal ensemble. We observe
respectively, with other methods making no progress past the that performance improves drastically from 1% at k = 1 to
first stage. We attribute the poor performance of prior methods 44% at k =100, then slightly tapers down with higher k. This
to compounding errors and non-Markovian behavior in the illustrates that more chunking and a lower effective horizon
data: the behavior degrades significantly towards the end of generally improve performance. We attribute the slight dip at
an episode, and the robot can pause indefinitely for certain k =200,400 (i.e., close to open-loop control) to the lack of
states. ACT mitigates both issues with action chunking. Our reactive behavior and the difficulty in modeling long action
ablations in Subsection VI-A also shows that chunking can sequences. To further evaluate the effectiveness and generality
significantlyimprovethesepriormethodswhenincorporated.In of action chunking, we augment two baseline methods with
addition,wenoticeadropinperformanceforallmethodswhen action chunking. For BC-ConvMLP, we simply increase the
switching from scripted data to human data in simulated tasks: outputdimensiontok∗action_dim,andforVINN,weretrieve
the stochasticity and multi-modality of human demonstrations the next k actions. We visualize their performance in Figure 8
make imitation learning a lot harder. (a)withdifferentk,showingtrendsconsistentwithACT,where
We report the success rate of the 3 remaining real-world more action chunking improves performance. While ACT still
tasks in Table II. For these tasks, we only compare with BeT, outperformsbothaugmentedbaselineswithsizablegains,these
which has the highest task success rate so far. Our method results suggest that action chunking is generally beneficial for
ACT reaches 84% success for Cup Open, 20% for Thread imitation learning in these settings.
Velcro, 64% for Prep Tape and 92% for Put On Shoe, again We then ablate the temporal ensemble by comparing the
outperforming BeT, which achieve zero final success on these highest success rate with or without it, again across the 4
challenging tasks. We observe relatively low success of ACT aforementionedtasksanddifferentk.Wenotethatexperiments
in Thread Velcro, where the success rate decreased by roughly with and without the temporal ensemble are separately tuned:
half at every stage, from 92% success at the first stage to hyperparameters that work best for no temporal ensemble may
20% final success. The failure modes we observe are 1) at not be optimal with a temporal ensemble. In Figure 8 (b), we
stage 2, the right arm closes its gripper too early and fails to showthatBC-ConvMLPbenefitsfromtemporalensemblingthe
grasp the tail of the cable tie mid-air, and 2) in stage 3, the most with a 4% gain, followed by a 3.3% gain for our method.
insertion is not precise enough and misses the loop. In both We notice a performance drop for VINN, a non-parametric
cases, it is hard to determine the exact position of the cable tie method. We hypothesize that a temporal ensemble mostly
from image observations: the contrast is low between the black benefits parametric methods by smoothing out the modeling
cable tie and the background, and the cable tie only occupies errors. In contrast, VINN retrieves ground-truth actions from
a small fraction of the image. We include examples of image the dataset and does not suffer from this issue.
observations in Appendix B.
B. Training with CVAE
VI. ABLATIONS
We train ACT with CVAE objective to model human
ACT employs action chunking and temporal ensembling to demonstrations, which can be noisy and contain multi-modal
mitigate compounding errors and better handle non-Markovian behavior. In this section, we compare with ACT without the
demonstrations. It also trains the policy as a conditional VAE CVAE objective, which simply predicts a sequence of actions
to model the noisy human demonstrations. In this section, we givencurrentobservation,andtrainedwithL1loss.InFigure8

--- Page 10 ---
Table 1 Table 1-1-1
Table 1-1
1 10 100 200 400 With CVAE No CVAE
Ours 1 21 44 42 41 no TE with TE Scripted Data 59 58
BC-ConvMLP 1 1 24 25 20 Ours 44 47.3 Human Data 35.3 2
VINN 0 6 23 27.25 37 BC-ConvMLP 25 29
VINN 37 17
50 50 +3.3% 60 -1%
37.5 37.5 45
+4%
25 25 30
-20%
12.5 12.5 15
-33.3%
0 0 0 1 10 100 200 400 Ours BC-ConvMLP VINN Scripted Data Human Data
fully-closed-loop fully-open-loop 5Hz 50Hz 5Hz 50Hz
Ours BC-ConvMLP VINN no TE with TE With CVAE No CVAE
(a) (b) (c) (d)
)%(
sseccus
)%(
sseccus
)%(
sseccus
k
thread zip tie unstack cups
)ces(
noitarud
***
70 35
60
30
50 25
40 20
30 15
20 10
10 5
Fig. 8: (a) We augment two baselines with action chunking, with different values of chunk size k on the x-axis, and success rate on the
y-axis. Both methods significantly benefit from action chunking, suggesting that it is a generally useful technique. (b) Temporal Ensemble
(TE) improves our method and BC-ConvMLP, while hurting VINN. (c) We compare with and without the CVAE training, showing that it is
crucial when learning from human data. (d) We plot the distribution of task completion time in our user study, where we task participants to
perform two tasks, at 5Hz or 50Hz teleoperation frequency. Lowering the frequency results in a 62% slowdown in completion time.
(c),wevisualizethesuccessrateaggregatedacross2simulated learning algorithm ACT. The synergy between these two parts
tasks, and separately plot training with scripted data and with allows us to learn fine manipulation skills directly in the real-
human data. We can see that when training on scripted data, world,suchasopeningatranslucentcondimentcupandslotting
the removal of CVAE objective makes almost no difference in a battery with a 80-90% success rate and around 10 min of
performance, because dataset is fully deterministic. While for demonstrations. While the system is quite capable, there exist
humandata,thereisasignificantdropfrom35.3%to2%.This tasks that are beyond the capability of either the robots or
illustrates that the CVAE objective is crucial when learning the learning algorithm, such as buttoning up a dress shirt.
from human demonstrations. We include a more detailed discussion about limitations in
Appendix F. Overall, we hope that this low-cost open-source
C. Is High-Frequency Necessary?
system represents an important step and accessible resource
Lastly, we conduct a user study to illustrate the necessity
towards advancing fine-grained robotic manipulation.
of high-frequency teleoperation for fine manipulation. With
the same hardware setup, we lower the frequency from 50Hz
ACKNOWLEDGEMENT
to 5Hz, a control frequency that is similar to recent works We thank members of the IRIS lab at Stanford for their
that use high-capacity deep networks for imitation learning support and feedback. We also thank Siddharth Karamcheti,
[7, 70]. We pick two fine-grained tasks: threading a zip cable Toki Migimatsu, Staven Cao, Huihan Liu, Mandi Zhao, Pete
tie and un-stacking two plastic cups. Both require millimeter- Florence and Corey Lynch for helpful discussions. Tony Zhao
level precision and closed-loop visual feedback. We perform is supported by Stanford Robotics Fellowship sponsored by
the study with 6 participants who have varying levels of FANUC, in addition to Schmidt Futures and ONR Grant
experience with teleoperation, though none had used ALOHA N00014-21-1-2685.
before. The participants were recruited from among computer
REFERENCES
sciencegraduatestudents,with4menand2womenaged22-25
[1] Viperx 300 robot arm 6dof. URL https://www.
The order of tasks and frequencies are randomized for each
trossenrobotics.com/viperx-300-robot-arm-6dof.aspx.
participant,andeachparticipantwasprovidedwitha2minutes
[2] Widowx 250 robot arm 6dof. URL https://www.
practiceperiodbeforeeachtrial.Werecordedthetimeittookto
trossenrobotics.com/widowx-250-robot-arm-6dof.aspx.
perform the task for 3 trials, and visualize the data in Figure 8
[3] Highlydexterousmanipulationsystem-capabilities-part
(d). On average, it took 33s for participants to thread the zip
1, Nov 2014. URL https://www.youtube.com/watch?v=
tie at 5Hz, which is lowered to 20s at 50Hz. For separating
TearcKVj0iY.
plastic cups, increasing the control frequency lowered the task
[4] Assembly performance metrics and test
duration from 16s to 10s. Overall, our setup (i.e. 50Hz) allows
methods, Apr 2022. URL https://www.
theparticipantstoperformhighlydexterousandprecisetasksin
nist.gov/el/intelligent-systems-division-73500/
a short amount of time. However, reducing the frequency from
robotic-grasping-and-manipulation-assembly/assembly.
50Hzto5Hzresultsina62%increaseinteleoperationtime.We
[5] Teleoperated robots - shadow teleoperation system, Nov
then use “Repeated Measures Designs”, a statistical procedure,
2022. URL https://www.shadowrobot.com/teleoperation/.
to formally verify that 50Hz teleoperation outperforms 5Hz
[6] Sridhar Pandian Arunachalam, Irmak Güzey, Soumith
with p-value <0.001. We include more details about the study
Chintala, and Lerrel Pinto. Holo-dex: Teaching dex-
in Appendix E.
terity with immersive mixed reality. arXiv preprint
VII. LIMITATIONSANDCONCLUSION arXiv:2210.06463, 2022.
We present a low-cost system for fine manipulation, com- [7] Anthony Brohan, Noah Brown, Justice Carbajal, Yev-
prising a teleoperation system ALOHA and a novel imitation gen Chebotar, Joseph Dabis, Chelsea Finn, Keerthana

--- Page 11 ---
Gopalakrishnan, Karol Hausman, Alexander Herzog, Ashwin Balakrishna, Daniel Seita, Jennifer Grannen,
JasmineHsu,JulianIbarz,BrianIchter,AlexIrpan,Tomas Minho Hwang, Ryan Hoque, Joseph Gonzalez, Nawid
Jackson, Sally Jesmonth, Nikhil J. Joshi, Ryan C. Julian, Jamali, Katsu Yamane, Soshi Iba, and Ken Goldberg.
Dmitry Kalashnikov, Yuheng Kuang, Isabel Leal, Kuang- Learning dense visual correspondences in simulation to
Huei Lee, Sergey Levine, Yao Lu, Utsav Malla, Deek- smooth and fold real fabrics. 2021 IEEE International
sha Manjunath, Igor Mordatch, Ofir Nachum, Carolina Conference on Robotics and Automation (ICRA), pages
Parada,JodilynPeralta,EmilyPerez,KarlPertsch,Jornell 11515–11522, 2020.
Quiambao, Kanishka Rao, Michael S. Ryoo, Grecia [19] Jennifer Grannen, Priya Sundaresan, Brijen Thananjeyan,
Salazar, Pannag R. Sanketi, Kevin Sayed, Jaspiar Singh, Jeffrey Ichnowski, Ashwin Balakrishna, Minho Hwang,
Sumedh Anand Sontakke, Austin Stone, Clayton Tan, Vainavi Viswanath, Michael Laskey, Joseph Gonzalez,
Huong Tran, Vincent Vanhoucke, Steve Vega, Quan Ho and Ken Goldberg. Untangling dense knots by learning
Vuong, F. Xia, Ted Xiao, Peng Xu, Sichun Xu, Tianhe task-relevantkeypoints. InConferenceonRobotLearning,
Yu, and Brianna Zitkovich. Rt-1: Robotics transformer 2020.
for real-world control at scale. ArXiv, abs/2212.06817, [20] Huy Ha and Shuran Song. Flingbot: The unreasonable
2022. effectivenessofdynamicmanipulationforclothunfolding.
[8] NicolasCarion,FranciscoMassa,GabrielSynnaeve,Nico- ArXiv, abs/2105.03655, 2021.
las Usunier, Alexander Kirillov, and Sergey Zagoruyko. [21] AnkurHanda,KarlVanWyk,WeiYang,JackyLiang,Yu-
End-to-end object detection with transformers. ArXiv, Wei Chao, Qian Wan, Stan Birchfield, Nathan D. Ratliff,
abs/2005.12872, 2020. and Dieter Fox. Dexpilot: Vision-based teleoperation
[9] Yuanpei Chen, Yaodong Yang, Tianhao Wu, Shengjie of dexterous robotic hand-arm system. 2020 IEEE
Wang, Xidong Feng, Jiechuan Jiang, Stephen McAleer, International Conference on Robotics and Automation
Hao Dong, Zongqing Lu, and Song-Chun Zhu. Towards (ICRA), pages 9164–9170, 2019.
human-level bimanual dexterous manipulation with rein- [22] Kaiming He, X. Zhang, Shaoqing Ren, and Jian Sun.
forcement learning. ArXiv, abs/2206.08686, 2022. Deep residual learning for image recognition. 2016 IEEE
[10] Rohan Chitnis, Shubham Tulsiani, Saurabh Gupta, and Conference on Computer Vision and Pattern Recognition
Abhinav Kumar Gupta. Efficient bimanual manipulation (CVPR), pages 770–778, 2015.
using learned task schemas. 2020 IEEE International [23] Irina Higgins, Loïc Matthey, Arka Pal, Christopher P.
Conference on Robotics and Automation (ICRA), pages Burgess, Xavier Glorot, Matthew M. Botvinick, Shakir
1149–1155, 2019. Mohamed, and Alexander Lerchner. beta-vae: Learning
[11] Sudeep Dasari and Abhinav Kumar Gupta. Transformers basic visual concepts with a constrained variational
for one-shot visual imitation. In Conference on Robot framework. In International Conference on Learning
Learning, 2020. Representations, 2016.
[12] Pim de Haan, Dinesh Jayaraman, and Sergey Levine. [24] Ryan Hoque, Ashwin Balakrishna, Ellen R. Novoseller,
Causal confusion in imitation learning. In Neural Albert Wilcox, Daniel S. Brown, and Ken Goldberg.
Information Processing Systems, 2019. Thriftydagger: Budget-aware novelty and risk gating for
[13] Jacob Devlin, Ming-Wei Chang, Kenton Lee, and interactive imitation learning. In Conference on Robot
Kristina Toutanova. Bert: Pre-training of deep bidirec- Learning, 2021.
tional transformers for language understanding. ArXiv, [25] Stephen James, Michael Bloesch, and Andrew J. Davison.
abs/1810.04805, 2019. Task-embedded control networks for few-shot imitation
[14] Yan Duan, Marcin Andrychowicz, Bradly C. Stadie, learning. ArXiv, abs/1810.03237, 2018.
Jonathan Ho, Jonas Schneider, Ilya Sutskever, P. Abbeel, [26] Eric Jang, Alex Irpan, Mohi Khansari, Daniel Kappler,
and Wojciech Zaremba. One-shot imitation learning. Frederik Ebert, Corey Lynch, Sergey Levine, and Chelsea
ArXiv, abs/1703.07326, 2017. Finn. Bc-z: Zero-shot task generalization with robotic
[15] Frederik Ebert, Yanlai Yang, Karl Schmeckpeper, imitation learning. In Conference on Robot Learning,
BernadetteBucher,GeorgiosGeorgakis,KostasDaniilidis, 2022.
Chelsea Finn, and Sergey Levine. Bridge data: Boosting [27] R G Jenness and C D Wicker. Master–slave manipulators
generalizationofroboticskillswithcross-domaindatasets. and remote maintenance at the oak ridge national labora-
ArXiv, abs/2109.13396, 2021. tory, Jan 1975. URL https://www.osti.gov/biblio/4179544.
[16] PeterR.Florence,LucasManuelli,andRussTedrake.Self- [28] Edward Johns. Coarse-to-fine imitation learning: Robot
supervised correspondence in visuomotor policy learning. manipulation from a single demonstration. 2021 IEEE
IEEE Robotics and Automation Letters, 5:492–499, 2019. International Conference on Robotics and Automation
[17] Peter R. Florence, Corey Lynch, Andy Zeng, Oscar (ICRA), pages 4613–4619, 2021.
Ramirez, Ayzaan Wahid, Laura Downs, Adrian S. Wong, [29] Liyiming Ke, Jingqiang Wang, Tapomayukh Bhattachar-
Johnny Lee, Igor Mordatch, and Jonathan Tompson. jee, Byron Boots, and Siddhartha Srinivasa. Grasping
Implicit behavioral cloning. ArXiv, abs/2109.00137,2021. with chopsticks: Combating covariate shift in model-free
[18] Aditya Ganapathi, Priya Sundaresan, Brijen Thananjeyan, imitation learning for fine manipulation. In International

--- Page 12 ---
Conference on Robotics and Automation (ICRA), 2021. Schaal. Learning and generalization of motor skills by
[30] Michael Kelly, Chelsea Sidrane, K. Driggs-Campbell, learning from demonstration. 2009 IEEE International
and Mykel J. Kochenderfer. Hg-dagger: Interactive Conference on Robotics and Automation, pages 763–768,
imitationlearningwithhumanexperts. 2019International 2009.
Conference on Robotics and Automation (ICRA), pages [44] DeanA.Pomerleau. Alvinn:Anautonomouslandvehicle
8077–8083, 2018. in a neural network. In NIPS, 1988.
[31] Heecheol Kim, Yoshiyuki Ohmura, and Yasuo Kuniyoshi. [45] Yuzhe Qin, Hao Su, and Xiaolong Wang. From one
Gaze-based dual resolution deep imitation learning for hand to multiple hands: Imitation learning for dexterous
high-precision dexterous robot manipulation. IEEE manipulation from single-camera teleoperation. IEEE
Robotics and Automation Letters, 6:1630–1637, 2021. Robotics and Automation Letters, 7:10873–10881, 2022.
[32] Heecheol Kim, Yoshiyuki Ohmura, and Yasuo Kuniyoshi. [46] Rouhollah Rahmatizadeh, Pooya Abolghasemi, Ladislau
Robot peels banana with goal-conditioned dual-action Bölöni, and Sergey Levine. Vision-based multi-task
deep imitation learning. ArXiv, abs/2203.09749, 2022. manipulation for inexpensive robots using end-to-end
[33] Diederik P. Kingma and Max Welling. Auto-encoding learning from demonstration. 2018 IEEE International
variational bayes. CoRR, abs/1312.6114, 2013. Conference on Robotics and Automation (ICRA), pages
[34] Oliver Kroemer, Christian Daniel, Gerhard Neumann, 3758–3765, 2017.
Herke van Hoof, and Jan Peters. Towards learning [47] Stéphane Ross, Geoffrey J. Gordon, and J. Andrew
hierarchical skills for multi-phase manipulation tasks. Bagnell. A reduction of imitation learning and structured
2015 IEEE International Conference on Robotics and prediction to no-regret online learning. In International
Automation (ICRA), pages 1503–1510, 2015. Conference on Artificial Intelligence and Statistics, 2010.
[35] LucyLai,AnnZHuang,andSamuelJGershman. Action [48] SeyedSinaMirrazaviSalehian,NadiaFigueroa,andAude
chunkingaspolicycompression,Sep2022. URLpsyarxiv. Billard. A unified framework for coordinated multi-arm
com/z8yrv. motion planning. The International Journal of Robotics
[36] MichaelLaskey,JonathanLee,RoyFox,AncaD.Dragan, Research, 37:1205 – 1232, 2018.
and Ken Goldberg. Dart: Noise injection for robust [49] Nur Muhammad (Mahi) Shafiullah, Zichen Jeff Cui,
imitation learning. In Conference on Robot Learning, Ariuntuya Altanzaya, and Lerrel Pinto. Behavior trans-
2017. formers: Cloning k modes with one stone. ArXiv,
[37] Alex X. Lee, Henry Lu, Abhishek Gupta, Sergey Levine, abs/2206.11251, 2022.
and P. Abbeel. Learning force-based manipulation [50] Kaushik Shivakumar, Vainavi Viswanath, Anrui Gu,
of deformable objects from multiple demonstrations. Yahav Avigal, Justin Kerr, Jeffrey Ichnowski, Richard
2015 IEEE International Conference on Robotics and Cheng, Thomas Kollar, and Ken Goldberg. Sgtm 2.0:
Automation (ICRA), pages 177–184, 2015. Autonomously untangling long cables using interactive
[38] Weiwei Li. Optimal control for biological movement perception. ArXiv, abs/2209.13706, 2022.
systems. 2006. [51] Mohit Shridhar, Lucas Manuelli, and Dieter Fox. Cliport:
[39] Ajay Mandlekar, Danfei Xu, J. Wong, Soroush Nasiriany, Whatandwherepathwaysforroboticmanipulation.ArXiv,
Chen Wang, Rohun Kulkarni, Li Fei-Fei, Silvio Savarese, abs/2109.12098, 2021.
Yuke Zhu, and Roberto Mart’in-Mart’in. What matters [52] Mohit Shridhar, Lucas Manuelli, and Dieter Fox.
in learning from offline human demonstrations for robot Perceiver-actor: A multi-task transformer for robotic
manipulation. In Conference on Robot Learning, 2021. manipulation. ArXiv, abs/2209.05451, 2022.
[40] KunalMenda,K.Driggs-Campbell,andMykelJ.Kochen- [53] Aravind Sivakumar, Kenneth Shaw, and Deepak Pathak.
derfer. Ensembledagger: A bayesian approach to safe Robotic telekinesis: Learning a robotic hand imitator by
imitation learning. 2019 IEEE/RSJ International Confer- watching humans on youtube. RSS, 2022.
ence on Intelligent Robots and Systems (IROS), pages [54] Christian Smith, Yiannis Karayiannidis, Lazaros Nal-
5041–5048, 2018. pantidis, Xavi Gratal, Peng Qi, Dimos V. Dimarogonas,
[41] Samuel Paradis, Minho Hwang, Brijen Thananjeyan, and Danica Kragic. Dual arm manipulation - a survey.
Jeffrey Ichnowski, Daniel Seita, Danyal Fer, Thomas Robotics Auton. Syst., 60:1340–1353, 2012.
Low, Joseph Gonzalez, and Ken Goldberg. Intermittent [55] Kihyuk Sohn, Honglak Lee, and Xinchen Yan. Learning
visual servoing: Efficiently learning policies robust to structured output representation using deep conditional
instrument changes for high-precision surgical manipula- generative models. In NIPS, 2015.
tion. 2021 IEEE International Conference on Robotics [56] srcteam. Shadow teleoperation system plays jenga,
and Automation (ICRA), pages 7166–7173, 2020. Mar 2021. URL https://www.youtube.com/watch?v=
[42] JyothishPari,NurMuhammad,SridharPandianArunacha- 7K9brH27jvM.
lam, and Lerrel Pinto. The surprising effectiveness of [57] srcteam. How researchers are using shadow robot’s
representationlearningforvisualimitation. arXivpreprint technology, Jun 2022. URL https://www.youtube.com/
arXiv:2112.01511, 2021. watch?v=p36fYIoTD8M.
[43] Peter Pastor, Heiko Hoffmann, Tamim Asfour, and Stefan [58] srcteam. Shadow teleoperation system, Jun 2022. URL

--- Page 13 ---
https://www.youtube.com/watch?v=cx8eznfDUJA. review. Journal of Sport and Health Science, 2022. ISSN
[59] Simon Stepputtis, Maryam Bandari, Stefan Schaal, and 2095-2546. doi: https://doi.org/10.1016/j.jshs.2022.04.
Heni Ben Amor. A system for imitation learning 001. URL https://www.sciencedirect.com/science/article/
of contact-rich bimanual manipulation policies. 2022 pii/S2095254622000473.
IEEE/RSJ International Conference on Intelligent Robots
and Systems (IROS), pages 11810–11817, 2022.
[60] Priya Sundaresan, Jennifer Grannen, Brijen Thanan-
jeyan, Ashwin Balakrishna, Jeffrey Ichnowski, Ellen R.
Novoseller, Minho Hwang, Michael Laskey, Joseph Gon-
zalez, and Ken Goldberg. Untangling dense non-planar
knots by learning manipulation features and recovery
policies. ArXiv, abs/2107.08942, 2021.
[61] Gokul Swamy, Sanjiban Choudhury, J. Andrew Bagnell,
and Zhiwei Steven Wu. Causal imitation learning under
temporally correlated noise. In International Conference
on Machine Learning, 2022.
[62] NaftaliTishbyandNogaZaslavsky. Deeplearningandthe
information bottleneck principle. 2015 IEEE Information
Theory Workshop (ITW), pages 1–5, 2015.
[63] EmanuelTodorov,TomErez,andYuvalTassa. Mujoco:A
physics engine for model-based control. 2012 IEEE/RSJ
International Conference on Intelligent Robots and Sys-
tems, pages 5026–5033, 2012.
[64] Stephen Tu, Alexander Robey, Tingnan Zhang, and
N. Matni. On the sample complexity of stability con-
strained imitation learning. In Conference on Learning
for Dynamics & Control, 2021.
[65] Ashish Vaswani, Noam M. Shazeer, Niki Parmar, Jakob
Uszkoreit, Llion Jones, Aidan N. Gomez, Lukasz Kaiser,
and Illia Polosukhin. Attention is all you need. ArXiv,
abs/1706.03762, 2017.
[66] Solomon Wiznitzer, Luke Schmitt, and Matt Trossen.
interbotix_ros_manipulators. URL https://github.com/
Interbotix/interbotix_ros_manipulators.
[67] Fan Xie, A. M. Masum Bulbul Chowdhury, M. Clara
De Paolis Kaluza, Linfeng Zhao, Lawson L. S. Wong,
andRoseYu.Deepimitationlearningforbimanualrobotic
manipulation. ArXiv, abs/2010.05134, 2020.
[68] Andy Zeng, Peter R. Florence, Jonathan Tompson, Stefan
Welker,JonathanChien,MariaAttarian,TravisArmstrong,
Ivan Krasin, Dan Duong, Vikas Sindhwani, and Johnny
Lee. Transporter networks: Rearranging the visual world
for robotic manipulation. In Conference on Robot
Learning, 2020.
[69] Tianhao Zhang, Zoe McCarthy, Owen Jow, Dennis Lee,
Ken Goldberg, and P. Abbeel. Deep imitation learning
for complex manipulation tasks from virtual reality
teleoperation. 2018 IEEE International Conference on
Robotics and Automation (ICRA), pages 1–8, 2017.
[70] AllanZhou,MooJinKim,LiruiWang,PeterR.Florence,
and Chelsea Finn. Nerf in the palm of your hand:
Corrective augmentation for robotics via novel-view
synthesis. ArXiv, abs/2301.08556, 2023.
[71] Áron Horváth, Eszter Ferentzi, Kristóf Schwartz, Nina
Jacobs, Pieter Meyns, and Ferenc Köteles. The measure-
ment of proprioceptive accuracy: A systematic literature

--- Page 14 ---
APPENDIX pipette, writing, twisting open an aluminum case, and in-hand
rotation of Baoding balls. We are able to recreate 14 out of the
A. Comparing ALOHA with Prior Teleoperation Setups
15 tasks with similar objects and comparable amount of time.
InFigure9,weincludemoreteleoperatedtasksthatALOHA We cannot recreate the Baoding ball in-hand rotation task, as
is capable of. We stress that all objects are taken directly our setup does not have a hand.
from the real world without any modification, to demonstrate
ALOHA’s generality in real life settings. B. Example Image Observations
ALOHAexploitsthekinestheticsimilaritybetweenleaderand We include example image observations taken during policy
follower robots by using joint-space mapping for teleoperation. execution time in Figure 10, for each of the 6 real tasks. From
A leader-follower design choice dates back to at least as far as lefttoright,the4imagesarefromtopcamera,frontcamera,left
1953, when Central Research Laboratories built teleoperation wrist, and right wrist respectively. The top and front cameras
systems for handling hazardous material [27]. More recently, are static, while the wrist cameras move with the robots and
companieslikeRE2[3]alsobuilthighlydexterousteleoperation give detailed views of the gripper. We also rotate the front
systems with joint-space mapping. ALOHA is similar to these camera by 90 degrees to capture more vertical space. For all
previous systems, while benefiting significantly from recent cameras, the focal length is fixed with auto-exposure on to
advances of low-cost actuators and robot arms. It allows us to adjust for changing lighting conditions. All cameras steam at
achieve similar levels of dexterity with much lower cost, and 480×640 and 30fps.
also without specialized hardware or expert assembly.
C. Detailed Architecture Diagram
Next,wecomparethecostofALOHAtorecentteleoperation
systems. DexPilot [21] controls a dexterous hand using image WeincludeamoredetailedarchitecturediagraminFigure11.
streams of a human hand. It has 4 calibrated Intel Realsense to At training time, we first sample tuples of RGB images and
capture the point cloud of a human hand, and retarget the pose jointpositions,togetherwiththecorrespondingactionsequence
to an Allegro hand. The Allegro hand is then mounted to a as prediction target (Step 1: sample data). We then infer style
KUKA LBR iiwa7 R800. DexPilot allows for impressive tasks variable z using CVAE encoder shown in yellow (Step 2: infer
such as extracting money from a wallet, opening a penut jar, z). The input to the encoder are 1) the [CLS] token, which
and insertion tasks in NIST board #1. We estimate the system consists of learned weights that are randomly initialized, 2)
costtobearound$100kwithonearm+hand.Morerecentworks embedded joint positions, which are joint positions projected
such as Robotic Telekinesis [53, 6, 45] seek to reduce the cost to the embedding dimension using a linear layer, 3) embedded
of DexPilot by using a single RGB camera to detect hand action sequence, which is the action sequence projected to the
pose, and retarget using learning techniques. While sensing embedding dimension using another linear layer. These inputs
costisgreatlyreduced,thecostforrobothandandarmremains form a sequence of (k+2)×embedding_dimension, and
high: a dexterous hand has more degrees of freedom and is is processed with the transformer encoder. We only take the
naturally pricier. Moving the hand around would also require first output, which corresponds to the [CLS] token, and use
anindustrialarmwithatleast2kgpayload,increasingtheprice another linear network to predict the mean and variance of
further. We estimate the cost of these systems to be around z’s distribution, parameterizing it as a diagonal Gaussian. A
$18k with one arm+hand. Lastly, the Shadow Teleoperation sample of z is obtained using reparameterization, a standard
System is a bimanual system for teleoperating two dexterous way to allow back-propagating through the sampling process
hands. Both hands are mounted to a UR10 robot, and the hand so the encoder and decoder can be jointly optimized [33].
pose is obtained by either a tracking glove or a haptic glove. Next, we try to obtain the predicted action from CVAE
This system is the most capable among all aforementioned decoder i.e. the policy (Step 3: predict action sequence). For
works, benefitted from its bimanual design. However, it also each of the image observations, it is first processed by a
costs the most, at at least $400k. ALOHA, on the other hand, ResNet18 to obtain a feature map, and then flattened to
is a bimanual setup that costs $18k ($20k after adding optional get a sequence of features. These features are projected to
add-onssuchascameras).Reducingdexteroushandstoparallel the embedding dimension with a linear layer, and we add
jaw grippers allows us to use light-weight and low-cost robots, a 2D sinusoidal position embedding to perserve the spatial
which can be more nimble and require less service. information. The feature sequence from each camera is then
Finally,wecomparethecapabilitiesofALOHAwithprevious concatenated to be used as input to the transformer encoder.
systems. We choose the most capable system as reference: the Two additional inputs are joint positions and z, which are also
Shadow Teleoperation System [5], which costs more than 10x projected to the embedding dimension with two linear layers
of ALOHA. Specifically, we found three demonstration videos respectively. The output of the transformer encoder are then
[56, 57, 58] that contain 15 example use cases of the Shadow used as both “keys” and “values” in cross attention layers of
Teleoperation System, and seek to recreate them using ALOHA. the transformer decoder, which predicts action sequence given
The tasks include playing “beer pong”, “jenga,” and a rubik’s encoder output. The “queries” are fixed sinusoidal embeddings
cube, using a dustpan and brush, twisting open a water bottle, for the first layer.
pouring liquid out, untying velcro cable tie, picking up an egg At test time, the CVAE encoder (shown in yellow) is
and a light bulb, inserting and unplugging USB, RJ45, using a discarded and the CVAE decoder is used as the policy. The

--- Page 15 ---
Fig. 9: Teleoperation task examples with ALOHA. We include videos on the project website.
incoming observations (images and joints) are fed into the teleoperating robots with a VR controller, and the other 3 has
model in the same way as during training. The only difference nopriorexperienceteleoperating.Noneoftheparticipantsused
is in z, which represents the “style” of the action sequence ALOHA before. To implement the 5Hz version of ALOHA, we
we want to elicit from the policy. We simply set z to a zero readfromtheleaderrobotat5Hz,interpolateinthejointspace,
vector, which is the mean of the unit Gaussian prior used and send the interpolated positions to the robot at 50Hz. We
during training. Thus given an observation, the output of the choose tasks that emphasizes high-precision and close-loop
policy is always deterministic, benefiting policy evaluation. visual feedback. We include images of the objects used in
Figure 12. For threading zip cable tie, the hole measures 4mm
D. Experiment Details and Hyperparameters
x 1.5mm, and the cable tie measures 0.8mm x 3.5mm with a
We carefully tune the baselines and include the hyperparam- pointy tip. It is initially lying flat on the table, and the operator
eters used in Table III, IV, V, VI, VII. For BeT, we found needs to pick it up with one gripper, grasp the other end mid-
that increasing history length from 10 (as in original paper) to air, then coordinate both hands to insert one end of the cable
100greatlyimprovestheperformance.Largehiddendimension tie into the hole on the other end. For unstacking cup, we use
also generally helps. For VINN, the k used when retrieving two single-use plastic cups that has 2.5mm clearance between
nearestneighborisadaptivelychosenwiththelowestvalidation them when stacked. The teleoperator need to grasp the edge
loss, same as the original paper. We also found that using joint of upper cup, then either shake to separate or use the help
position differences in addition to visual feature similarity from the other gripper. During the user study, we randomize
improves performance when there is no action chunking, in the order in which operators attempt each task, and whether
which case we have state weight = 10 when retrieving actions. they use 50Hz or 5Hz controller first. We also randomize the
However, we found this to hurt performance with action initial position of the object randomly around the table center.
chunking and thus set state weight to 0 for action chunking For each setting, the operator has 2 minutes to adapt, followed
experiments. by 3 consecutive attempts of the task with duration recorded.
E. User Study Details
F. Limitations
We conduct the user study with 6 participants, recruited
from computer science graduate students, with 4 men and We now discuss limitations of the ALOHA hardware and
2 women aged 22-25. 3 of the participants had experience the policy learning with ACT.

--- Page 16 ---
Fig. 10: Image observation examples for 5 real-world tasks. The 4 columns are [top camera, front camera, left wrist camera, right wrist
camera] respectively. We rotate the front camera by 90 degree to capture more vertical space.
Hardware Limitations. On the hardware front, ALOHA the seam for prying open the candy wrapper could appear
struggles with tasks that require multiple fingers from both anywhere around the candy. During demonstration collection,
hands,forexampleopeningchild-proofpillbottleswithapush it is difficult even for human to discern. The operator needs to
tab. To open the bottle, one hand needs to hold the bottle and judge by looking at the graphics printed on the wrapper and
pushes down on the push tab, with the other hand twisting the find the discontinuity. We constantly observe the policy trying
lid open. ALOHA also struggles with tasks that require high to peel at places where the seam does not exist. To better track
amount of forces, for example lifting heavy objects, twisting the progress, we attempted another evaluation where we give
open a sealed bottle of water, or opening markers caps that are 10 trials for each candy, and repeat this for 5 candies. For this
tightly pressed together. This is because the low-cost motors protocol, our policy successfully unwraps 3/5 candies.
cannot generate enough torque to support these manipulations. Another task that ACT struggles with is opening a small
Tasks that requires finger nails are also difficult for ALOHA, ziploc bag laying flat on the table. The right gripper needs to
even though we design the grippers to be thin on the edge. firstpickitup,adjustitsothattheleftgrippercangraspfirmly
For example, we are not able to lift the edge of packing tape on the pulling region, followed by the right hand grasping
when it is taped onto itself, or opening aluminum soda cans. the other side of the pulling region, and pull it open. Our
policy trained with 50 demonstrations can consistently pick
PolicyLearningLimitations.Onthesoftwarefront,wereport up the bag, while having difficulties performing the following
all 2 tasks that we attempted where ACT failed to learn 3 mid-air manipulation steps. We hypothesize that the bag is
the behavior. The first one is unwrapping candies. The steps hard to perceive, and in addition, small differences in the pick
involves picking up the candy from the table, pull on both up position can affect how the bag deforms, and result in large
ends of it, and pry open the wrapper to expose the candy. We differences in where the pulling region ends up. We believe
collected 50 demonstrations to train the ACT policy. In our thatpretraining,moredata,andbetterperceptionarepromising
preliminary evaluation with 10 trials, the policy picks up the directions to tackle these extremely difficult tasks.
candy10/10,pullsonbothends8/10,whileunwrapsthecandy
0/10. We attribute the failure to the difficulty of perception and
lack of data. Specifically, after pulling the candy on both sides,

--- Page 17 ---
Training
Step 1: sample data
…
Demo sample
Dataset 4 RGB images , joints action sequence
4x (480x640x3) (14) (k x 14)
batch size
Step 2: infer z z_mean (32)
z_std (32) sample with
linear layer 4 reparametrization
512 -> 64
transformer
joints embedded joints
Weight matrix [CLS] (14) linear layer 2 (512) encoder
(512) (512) 14 -> 512
4x self-attention blocks
… …
+
…
action sequence embedded action sequence
(k x 14) l 1 i 4 n - e > a 5 r 1 l 2 ayer 1 S Po in s u it s i o o i n d a E l m bedding (k x 512) [C (5 L 12 S ) ]em j b o e in d t d s edembedded (k a x c 5 t 1 i 2 o ) n sequence
(512)
Step 3: predict action sequence
predicted action sequence
… … … …
1 15x20x728
flatten
2 300x728 transformer transformer
linear layer 5 encoder decoder
728 -> 512
3 4x self-attention blocks 7x cross-attention blocks
300x512
+ Sinusoidal
PosEmb
… … … …
4
ResNet18 cam 1 cam 4 position embeddings (fixed)
+Sinusoidal PosEmb linear layer 6 linear layer 7
14 -> 512 32 -> 512
joints
Testing
incoming
observations
predicted action sequence
… … … …
1 15x20x728
flatten
2 300x728 transformer transformer
linear layer 5 encoder decoder
728 -> 512
3 4x self-attention blocks 7x cross-attention blocks
300x512
+ Sinusoidal
PosEmb
… … … …
4
ResNet18 cam 1 cam 4 position embeddings (fixed)
+Sinusoidal PosEmb linear layer 6 linear layer 7
14 -> 512 32 -> 512
joints
joints
Fig. 11: Detail architecture of Action Chunking with Transformers (ACT).

--- Page 18 ---
Fig. 12: The cable tie and cups for user study.
learningrate 1e-5
batchsize 8
#encoderlayers 4
#decoderlayers 7
feedforwarddimension 3200
hiddendimension 512
#heads 8
chunksize 100
beta 10
dropout 0.1
TABLE III: Hyperparameters of ACT.
learningrate 3e-4
batchsize 128
epochs 100
momentum 0.9
weightdecay 1.5e-6
TABLE IV: Hyperparameters of BYOL, the feature extractor for VINN and BeT.
learningrate 1e-4
batchsize 64
#layers 6
#heads 6
hiddendimension 768
historylength 100
weightdecay 0.1
offsetlossscale 1000
focallossgamma 2
dropout 0.1
discretizer#bins 64
TABLE V: Hyperparameters of BeT.
k(nearestneighbour) adaptive
stateweight 0or10
TABLE VI: Hyperparameters of VINN.
learningrate 1e-5
batchsize 2
ViTdimhead 32
ViTwindowsize 7
ViTmbconvexpansionrate 4
ViTmbconvshrinkagerate 0.25
ViTdropout 0.1
RT-1depth 6
RT-1heads 8
RT-1dimhead 64
RT-1actionbins 256
RT-1conddropprob 0.2
RT-1tokenlearnernumoutputtokens 8
weightdecay 0
historylength 6
TABLE VII: Hyperparameters of RT-1.