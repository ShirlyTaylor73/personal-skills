--- Page 1 ---
.
Diffusion Policy: Visuomotor Policy
Learning via Action Diffusion
Cheng Chi∗1, Zhenjia Xu∗1, Siyuan Feng2, Eric Cousineau2, Yilun Du3, Benjamin Burchfiel2,
Russ Tedrake 2,3, Shuran Song1,4
Abstract
This paper introduces Diffusion Policy, a new way of generating robot behavior by representing a robot’s visuomotor
policy as a conditional denoising diffusion process. We benchmark Diffusion Policy across 15 different tasks from 4
differentrobotmanipulationbenchmarksandfindthatitconsistentlyoutperformsexistingstate-of-the-artrobotlearning
methods with an average improvement of 46.9%. Diffusion Policy learns the gradient of the action-distribution score
functionanditerativelyoptimizeswithrespecttothisgradientfieldduringinferenceviaaseriesofstochasticLangevin
dynamicssteps.Wefindthatthediffusionformulationyieldspowerfuladvantageswhenusedforrobotpolicies,including
gracefully handling multimodal action distributions, being suitable for high-dimensional action spaces, and exhibiting
impressive training stability. To fully unlock the potential of diffusion models for visuomotor policy learning on physical
robots,thispaperpresentsasetofkeytechnicalcontributionsincludingtheincorporationofrecedinghorizoncontrol,
visualconditioning,andthetime-seriesdiffusiontransformer.Wehopethisworkwillhelpmotivateanewgenerationof
policylearningtechniquesthatareabletoleveragethepowerfulgenerativemodelingcapabilitiesofdiffusionmodels.
Code,data,andtrainingdetailsisavailablediffusion-policy.cs.columbia.edu
Keywords
Imitationlearning,visuomotorpolicy,manipulation
Action
Representation
Scalar (Regression) Implicit Policy Diffusion Policy
Explicit Policy
Mixture of Gaussians iter
Categorical
(a) Explicit Policy (b) Implicit Policy (c) Diffusion Policy
Figure1. PolicyRepresentations.a)Explicitpolicywithdifferenttypesofactionrepresentations.b)Implicitpolicylearnsan
energyfunctionconditionedonbothactionandobservationandoptimizesforactionsthatminimizetheenergylandscapec)
Diffusionpolicyrefinesnopis(ae)intoactionsviaalearnedgradientfield.Thisformulationprovidesstabletraining,allowsthelearned
policytoaccuratelymodelmultimodalactiondistributions,andaccommodateshigh-dimensionalactionsequences.
1 Introduction generates behavior via a “conditional denoising diffusion
process Ho et al. (2020) on robot action space”, Diffusion
Policylearningfromdemonstration,initssimplestform,can
Policy. In this formulation, instead of directly outputting
beformulatedasthesupervisedregressiontaskoflearningto
an action, the policy infers the action-score gradient,
mapobservationstoactions.Inpracticehowever,theunique
conditioned on visual observations, for K denoising
nature of predicting robot actions — such as the existence
iterations (Fig. 1 c). This formulation allows robot policies
of multimodal distributions, sequential correlation, and the
to inherit several key properties from diffusion models –
requirementofhighprecision—makesthistaskdistinctand
significantlyimprovingperformance.
challengingcomparedtoothersupervisedlearningproblems.
Prior work attempts to address this challenge by
exploring different action representations (Fig 1 a) – using • Expressing multimodal action distributions. By
mixtures of Gaussians Mandlekar et al. (2021), categorical learning the gradient of the action score function
representationsofquantizedactionsShafiullahetal.(2022), Song and Ermon (2019) and performing Stochastic
orbyswitchingthethepolicyrepresentation(Fig1b)–from Langevin Dynamics sampling on this gradient field,
explicittoimplicittobettercapturemulti-modaldistributions Diffusion policy can express arbitrary normalizable
Florenceetal.(2021);Wuetal.(2020). distributions Neal et al. (2011), which includes mul-
In this work, we seek to address this challenge by timodal action distributions, a well-known challenge
introducing a new form of robot visuomotor policy that forpolicylearning.
4202
raM
41
]OR.sc[
5v73140.3032:viXra

--- Page 2 ---
2
• High-dimensionaloutputspace.Asdemonstratedby providing strong evidence of the effectiveness of Diffusion
their impressive image generation results, diffusion Policy. We also provide detailed analysis to carefully
models have shown excellent scalability to high- examine the characteristics of the proposed algorithm and
dimension output spaces. This property allows the theimpactsofthekeydesigndecisions.
policy to jointly infer a sequence of future actions Thisworkisanextendedversionoftheconferencepaper
instead of single-step actions, which is critical for Chietal.(2023).Weexpandthecontentofthispaperinthe
encouragingtemporalactionconsistencyandavoiding followingways:
myopicplanning.
• Include a new discussion section on the connections
• Stabletraining.Trainingenergy-basedpoliciesoften betweendiffusionpolicyandcontroltheory.SeeSec.
requires negative sampling to estimate an intractable 4.5.
normalization constant, which is known to cause
training instability Du et al. (2020); Florence et al. • Include additional ablation studies in simulation on
(2021). Diffusion Policy bypasses this requirement alternative network architecture design and different
by learning the gradient of the energy function and pretrainingandfinetuningparadigms,Sec.5.4.
thereby achieves stable training while maintaining
distributionalexpressivity. • Extend the real-world experimental results with three
bimanual manipulation tasks including Egg Beater,
Our primary contribution is to bring the above
MatUnrolling,andShirtFoldinginSec.7.
advantages to the field of robotics and demonstrate their
effectiveness on complex real-world robot manipulation Thecode,data,andtrainingdetailsarepubliclyavailable
tasks. To successfully employ diffusion models for for reproducing our results diffusion-policy.cs.
visuomotor policy learning, we present the following columbia.edu.
technical contributions that enhance the performance of
Diffusion Policy and unlock its full potential on physical
2 Diffusion Policy Formulation
robots:
We formulate visuomotor robot policies as Denoising
• Closed-loop action sequences. We combine the
Diffusion Probabilistic Models (DDPMs) Ho et al. (2020).
policy’s capability to predict high-dimensional action
Crucially, Diffusion policies are able to express complex
sequences with receding-horizon control to achieve
multimodal action distributions and possess stable training
robust execution. This design allows the policy to
behavior – requiring little task-specific hyperparameter
continuouslyre-planitsactioninaclosed-loopmanner
tuning. The following sections describe DDPMs in more
while maintaining temporal action consistency –
detail and explain how they may be adapted to represent
achieving a balance between long-horizon planning
visuomotorpolicies.
andresponsiveness.
• Visual conditioning. We introduce a vision- 2.1 Denoising Diffusion Probabilistic Models
conditioned diffusion policy, where the visual
DDPMs are a class of generative model where the output
observations are treated as conditioning instead of a
generation is modeled as a denoising process, often called
part of the joint data distribution. In this formulation,
StochasticLangevinDynamicsWellingandTeh(2011).
the policy extracts the visual representation once
StartingfromxKsampledfromGaussiannoise,theDDPM
regardless of the denoising iterations, which
performs K iterations of denoising to produce a series
drastically reduces the computation and enables
of intermediate actions with decreasing levels of noise,
real-timeactioninference.
xk,xk−1...x0, until a desired noise-free output x0 is formed.
• Time-series diffusion transformer. We propose Theprocessfollowstheequation
a new transformer-based diffusion network that
xk−1=α(xk−γε (xk,k)+N (cid:0) 0,σ2I (cid:1) ), (1)
minimizes the over-smoothing effects of typical θ
CNN-based models and achieves state-of-the-art
whereε isthenoisepredictionnetworkwithparametersθ
θ
performance on tasks that require high-frequency that will be optimized through learning and N (cid:0) 0,σ2I (cid:1) is
actionchangesandvelocitycontrol.
Gaussiannoiseaddedateachiteration.
We systematically evaluate Diffusion Policy across 15 The above equation 1 may also be interpreted as a single
tasks from 4 different benchmarks Florence et al. (2021); noisygradientdescentstep:
Gupta et al. (2019); Mandlekar et al. (2021); Shafiullah x′=x−γ∇E(x), (2)
et al. (2022) under the behavior cloning formulation.
The evaluation includes both simulated and real-world where the noise prediction network ε (x,k) effectively
θ
environments,2DoFto6DoFactions,single-andmulti-task predictsthegradientfield∇E(x),andγ isthelearningrate.
benchmarks, and fully- and under-actuated systems, with Thechoiceofα,γ,σ asfunctionsofiterationstepk,also
rigid and fluid objects, using demonstration data collected called noise schedule, can be interpreted as learning rate
bysingleandmultipleusers. schedulingingradientdecentprocess.Anα slightlysmaller
Empirically,wefindconsistentperformanceboostacross than1hasbeenshowntoimprovestabilityHoetal.(2020).
all benchmarks with an average improvement of 46.9%, DetailsaboutnoiseschedulewillbediscussedinSec3.3.

--- Page 3 ---
DiffusionPolicy 3
Input: Image Observation Sequence
…
Conv1D Cross Attention
Conv1D
Conv1D
Conv1D
Conv1D
Output: Action Sequence b) CNN-based c) Transformer-based
Cross
Attention
×K Obs
Emb
Action Emb
Action Emb
A
Emb
…
a
b
x: Action Emb ×K
a
b
x: Action Emb
r a e
n i L
Linear
∇E(At) ∇E(At)
a ⋅ x + b
a ⋅ x + b
At At
a) Diffusion Policy General Formulation
Observation
Ot
Observation
Ot
FiLM
conditioning
k
k
Observation O t O t+4
o o o o
Robot t-2 t-1 t t+4
Pose
Diffusion Policy
O
t
a a a a t t+1 t+2 t+3
Action Sequence A t
Prediction Horizon Tp
A t+4
AK
t
A3
t
A0
t
a
t+4
Figure2. DiffusionPolicyOverview a)Generalformulation.Attimestept,thepolicytakesthelatestTostepsofobservation
dataOt asinputandoutputsTastepsofactionsAt.b)IntheCNN-basedDiffusionPolicy,FiLM(Feature-wiseLinearModulation)
Perezetal.(2018)conditioningoftheobservationfeatureOt isappliedtoeveryconvolutionlayer,channel-wise.StartingfromA
t
K
drawnfromGaussiannoise,theoutputofnoise-predictionnetworkε issubtracted,repeatingKtimestogetA0,thedenoised
θ t
actionsequence.c)IntheTransformer-basedVaswanietal.(2017)DiffusionPolicy,theembeddingofobservationOt ispassed
intoamulti-headcross-attentionlayerofeachtransformerdecoderblock.Eachactionembeddingisconstrainedtoonlyattendto
itselfandpreviousactionembeddings(causalattention)usingtheattentionmaskillustrated.
2.2 DDPM Training Visual observation conditioning: We use a DDPM to
approximatetheconditionaldistribution p(A|O)insteadof
Thetrainingprocessstartsbyrandomlydrawingunmodified t t
examples, x0, from the dataset. For each sample, we thejointdistribution p(A t ,O t )usedinJanneretal.(2022a)
for planning. This formulation allows the model to predict
randomly select a denoising iteration k and then sample a
random noise εk with appropriate variance for iteration k. actions conditioned on observations without the cost of
inferringfuturestates,speedingupthediffusionprocessand
The noise prediction network is asked to predict the noise
improvingtheaccuracyofgeneratedactions.Tocapturethe
fromthedatasamplewithnoiseadded.
conditionaldistribution p(A|O),wemodifyEq1to:
t t
L =MSE(εk,ε (x0+εk,k)) (3)
θ
Ak−1=α(Ak−γε (O,Ak,k)+N (cid:0) 0,σ2I (cid:1) ) (4)
AsshowninHoetal.(2020),minimizingthelossfunction t t θ t t
in Eq 3 also minimizes the variational lower bound of the
ThetraininglossismodifiedfromEq3to:
KL-divergence between the data distribution p(x0) and the
distribution of samples drawn from the DDPM q(x0) using L =MSE(εk,ε (O,A0+εk,k)) (5)
θ t t
Eq1.
TheexclusionofobservationfeaturesO fromtheoutput
t
2.3 Diffusion for Visuomotor Policy Learning of the denoising process significantly improves inference
While DDPMs are typically used for image generation (x speed and better accommodates real-time control. It also
is an image), we use a DDPM to learn robot visuomotor helps to make end-to-end training of the vision encoder
policies. This requires two major modifications in the feasible. Details about the visual encoder are described in
formulation: 1. changing the output x to represent robot Sec.3.2.
actions. 2. making the denoising processes conditioned on
inputobservationO t .Thefollowingparagraphsdiscusseach 3 Key Design Decisions
ofthemodifications,andFig.2showsanoverview.
In this section, we describe key design decisions for
Closed-loop action-sequence prediction: An effective
Diffusion Policy as well as its concrete implementation of
action formulation should encourage temporal consistency
ε withneuralnetworkarchitectures.
and smoothness in long-horizon planning while allowing θ
promptreactionstounexpectedobservations.Toaccomplish
3.1 Network Architecture Options
this goal, we commit to the action-sequence prediction
produced by a diffusion model for a fixed duration before The first design decision is the choice of neural network
replanning. Concretely, at time step t the policy takes the architecturesforε .Inthiswork,weexaminetwocommon
θ
latest T steps of observation data O as input and predicts network architecture types, convolutional neural networks
o t
T stepsofactions,ofwhichT stepsofactionsareexecuted (CNNs) Ronneberger et al. (2015) and Transformers
p a
on the robot without re-planning. Here, we define T as Vaswani et al. (2017), and compare their performance
o
the observation horizon, T as the action prediction horizon and training characteristics. Note that the choice of noise
p
and T as the action execution horizon. This encourages prediction network ε is independent of visual encoders,
a θ
temporal action consistency while remaining responsive. whichwillbedescribedinSec.3.2.
MoredetailsabouttheeffectsofT arediscussedinSec4.3. CNN-based Diffusion Policy We adopt the 1D temporal
a
OurformulationalsoallowsrecedinghorizoncontrolMayne CNN from Janner et al. (2022b) with a few modifications:
and Michalska (1988) to futher improve action smoothness First, we only model the conditional distribution p(A|O)
t t
by warm-starting the next inference setup with previous byconditioningtheactiongenerationprocessonobservation
actionsequenceprediction. features O with Feature-wise Linear Modulation (FiLM)
t

--- Page 4 ---
4
Perez et al. (2018) as well as denoising iteration k, shown 3.3 Noise Schedule
in Fig 2 (b). Second, we only predict the action trajectory
The noise schedule, defined by σ, α, γ and the additive
instead of the concatenated observation action trajectory. Gaussian Noise εk as functions of k, has been actively
Third,weremovedinpainting-basedgoalstateconditioning
studied Ho et al. (2020); Nichol and Dhariwal (2021).
due to incompatibility with our framework utilizing a
The underlying noise schedule controls the extent to
receding prediction horizon. However, goal conditioning is
which diffusion policy captures high and low-frequency
stillpossiblewiththesameFiLMconditioningmethodused
characteristics of action signals. In our control tasks, we
forobservations.
empiricallyfoundthattheSquareCosineScheduleproposed
In practice, we found the CNN-based backbone to work in iDDPM Nichol and Dhariwal (2021) works best for our
wellonmosttasksoutoftheboxwithouttheneedformuch tasks.
hyperparameter tuning. However, it performs poorly when
the desired action sequence changes quickly and sharply 3.4 Accelerating Inference for Real-time
throughtime(suchasvelocitycommandactionspace),likely Control
due to the inductive bias of temporal convolutions to prefer
Weusethediffusionprocessasthepolicyforrobots;hence,
low-frequencysignalsTanciketal.(2020).
it is critical to have a fast inference speed for closed-loop
Time-series diffusion transformer To reduce the over-
real-time control. The Denoising Diffusion Implicit Models
smoothing effect in CNN models Tancik et al. (2020), we
(DDIM) approach Song et al. (2021) decouples the number
introduce a novel transformer-based DDPM which adopts
of denoising iterations in training and inference, thereby
the transformer architecture from minGPT Shafiullah et al.
allowing the algorithm to use fewer iterations for inference
(2022) for action prediction. Actions with noise Ak are
t to speed up the process. In our real-world experiments,
passed in as input tokens for the transformer decoder
using DDIM with 100 training iterations and 10 inference
blocks,withthesinusoidalembeddingfordiffusioniteration
iterations enables 0.1s inference latency on a Nvidia 3080
k prepended as the first token. The observation O is
t GPU.
transformed into observation embedding sequence by a
shared MLP, which is then passed into the transformer
4 Intriguing Properties of Diffusion Policy
decoderstackasinputfeatures.The“gradient”ε (O,Ak,k)
θ t t
is predicted by each corresponding output token of the Inthissection,weprovidesomeinsightsandintuitionsabout
decoderstack. diffusionpolicyanditsadvantagesoverotherformsofpolicy
representations.
In our state-based experiments, most of the best-
performing policies are achieved with the transformer
4.1 Model Multi-Modal Action Distributions
backbone, especially when the task complexity and rate of
action change are high. However, we found the transformer The challenge of modeling multi-modal distribution in
to be more sensitive to hyperparameters. The difficulty of human demonstrations has been widely discussed in
transformer training Liu et al. (2020) is not unique to behaviorcloningliteratureFlorenceetal.(2021);Shafiullah
Diffusion Policy and could potentially be resolved in the et al. (2022); Mandlekar et al. (2021). Diffusion Policy’s
future with improved transformer training techniques or ability to express multimodal distributions naturally and
increaseddatascale. preciselyisoneofitskeyadvantages.
Recommendations. In general, we recommend starting Intuitively, multi-modality in action generation for
withtheCNN-baseddiffusionpolicyimplementationasthe diffusion policy arises from two sources – an underlying
firstattemptatanewtask.Ifperformanceislowduetotask stochasticsamplingprocedureandastochasticinitialization.
complexityorhigh-rateactionchanges,thentheTime-series In Stochastic Langevin Dynamics, an initial sample A t K is
DiffusionTransformerformulationcanbeusedtopotentially drawn from standard Gaussian at the beginning of each
improveperformanceatthecostofadditionaltuning. sampling process, which helps specify different possible
convergence basins for the final action prediction A0. This
t
action is then further stochastically optimized, with added
Gaussian perturbations across a large number of iterations,
3.2 Visual Encoder
which enables individual action samples to converge and
move between different multi-modal action basins. Fig. 3,
The visual encoder maps the raw image sequence into
shows an example of the Diffusion Policy’s multimodal
a latent embedding O and is trained end-to-end with
t
behaviorinaplanarpushingtask(PushT,introducedbelow)
the diffusion policy. Different camera views use separate
withoutexplicitdemonstrationforthetestedscenario.
encoders, and images in each timestep are encoded
independentlyandthenconcatenatedtoformO.Weuseda
t
4.2 Synergy with Position Control
standardResNet-18(withoutpretraining)astheencoderwith
the following modifications: 1) Replace the global average We find that Diffusion Policy with a position-control
pooling with a spatial softmax pooling to maintain spatial actionspaceconsistentlyoutperformsDiffusionPolicywith
informationMandlekaretal.(2021).2)ReplaceBatchNorm velocity control, as shown in Fig 4. This surprising result
with GroupNorm Wu and He (2018) for stable training. standsincontrasttothemajorityofrecentbehaviorcloning
This is important when the normalization layer is used in work that generally relies on velocity control Mandlekar
conjunction with Exponential Moving Average He et al. et al. (2021); Shafiullah et al. (2022); Zhang et al. (2018);
(2020)(commonlyusedinDDPMs). Florence et al. (2019); Mandlekar et al. (2020b,a). We

--- Page 5 ---
DiffusionPolicy 5
Diffusion Policy LSTM-GMM BET IBC
Figure3. Multimodalbehavior.Atthegivenstate,the
end-effector(blue)caneithergoleftorrighttopushtheblock.
DiffusionPolicylearnsbothmodesandcommitstoonlyone
modewithineachrollout.Incontrast,bothLSTM-GMM
Mandlekaretal.(2021)andIBCFlorenceetal.(2021)are
biasedtowardonemode,whileBETShafiullahetal.(2022)fails
tocommittoasinglemodeduetoitslackoftemporalaction
consistency.Actionsgeneratedbyrollingout40stepsforthe
best-performingcheckpoint.
speculate that there are two primary reasons for this
discrepancy:First,actionmultimodalityismorepronounced
in position-control mode than it is when using velocity
control. Because Diffusion Policy better expresses action
multimodality than existing approaches, we speculate that
it is inherently less affected by this drawback than existing
methods. Furthermore, position control suffers less than
velocitycontrolfromcompoundingerroreffectsandisthus
moresuitableforaction-sequenceprediction(asdiscussedin
the following section). As a result, Diffusion Policy is both
less affected by the primary drawbacks of position control
andisbetterabletoexploitpositioncontrol’sadvantages.
    
    
    
    
    
    
 7 U Y E V I  / M X G L I R  T 
 I K R E L '  I X E 6  W W I G G Y 7  I Z M X E P I 6
• Temporalactionconsistency:TakeFig3asanexample.
To push the T block into the target from the bottom, the
policycangoaroundtheTblockfromeitherleftorright.
However,supposeeachactioninthesequenceispredicted
as independent multimodal distributions (as done in BC-
RNNandBET).Inthatcase,consecutiveactionscouldbe
drawnfromdifferentmodes,resultinginjitteryactionsthat
alternatebetweenthetwovalidtrajectories.
• Robustness to idle actions: Idle actions occur when
a demonstration is paused and results in sequences of
identical positional actions or near-zero velocity actions.
It is common during teleoperation and is sometimes
required for tasks like liquid pouring. However, single-
step policies can easily overfit to this pausing behavior.
For example, BC-RNN and IBC often get stuck in real-
worldexperimentswhentheidleactionsarenotexplicitly
removedfromtraining.
   
    
    
    
    
    
    
                    
 % G X M S R  , S V M ^ S R   W X I T W 
 : I P S G M X ]  Z W  4 S W M X M S R E P  ' S R X V S P
 0 7 8 1  + 1 1
 & ) 8
 ( M J J Y W M S R 4 S P M G ]  '
 ( M J J Y W M S R 4 S P M G ]  8
Figure4. Velocityv.s.PositionControl.Theperformance
differencewhenswitchingfromvelocitytopositioncontrol.
WhilebothBCRNNandBETperformancedecrease,Diffusion
Policyisabletoleveragetheadvantageofpositionandimprove
itsperformance.
4.3 Benefits of Action-Sequence Prediction
Sequencepredictionisoftenavoidedinmostpolicylearning
methods due to the difficulties in effectively sampling from
high-dimensional output spaces. For example, IBC would
struggle in effectively sampling high-dimensional action
space with a non-smooth energy landscape. Similarly, BC-
RNNandBETwouldhavedifficultyspecifyingthenumber
of modes that exist in the action distribution (needed for
GMMork-meanssteps).
In contrast, DDPM scales well with output dimensions
without sacrificing the expressiveness of the model, as
demonstrated in many image generation applications.
Leveragingthiscapability,DiffusionPolicyrepresentsaction
in the form of a high-dimensional action sequence, which
naturallyaddressesthefollowingissues:
 I K R E L '  J V I 4  I Z M X E P I 6
 % G X M S R  , S V M ^ S R  0 E X I R G ]  6 S F Y W X R I W W
               
 0 E X I R G ]   W X I T W 
 4 Y W L 8  7 U Y E V I
Figure5. DiffusionPolicyAblationStudy.Change
(difference)insuccessraterelativetothemaximumforeach
taskisshownontheY-axis.Left:trade-offbetweentemporal
consistencyandresponsivenesswhenselectingtheaction
horizon.Right:DiffusionPolicywithpositioncontrolisrobust
againstlatency.Latencyisdefinedasthenumberofsteps
betweenthelastframeofobservationstothefirstactionthat
canbeexecuted.
4.4 Training Stability
While IBC, in theory, should possess similar advantages
as diffusion policies. However, achieving reliable and high-
performance results from IBC in practice is challenging
due to IBC’s inherent training instability Ta et al.
(2022). Fig 6 shows training error spikes and unstable
evaluation performance throughout the training process,
making hyperparameter turning critical and checkpoint
selection difficult. As a result, Florence et al. (2021)
evaluate every checkpoint and report results for the best-
performingcheckpoint.Inareal-worldsetting,thisworkflow
necessitates the evaluation of many policies on hardware to
selectafinalpolicy.Here,wediscusswhyDiffusionPolicy
appearssignificantlymorestabletotrain.
Animplicitpolicyrepresentstheactiondistributionusing
anEnergy-BasedModel(EBM):
e−Eθ(o,a)
p (a|o)= (6) θ Z(o,θ)
whereZ(o,θ)isanintractablenormalizationconstant(with
respecttoa).

--- Page 6 ---
6
To train the EBM for implicit policy, an InfoNCE-style
loss function is used, which equates to the negative log-
likelihoodofEq6:
e−Eθ(o,a)
L =−log( ) (7)
infoNCE e−Eθ(o,a)+∑ Nnege−Eθ(o,(cid:101)aj)
j=1
whereasetofnegativesamples{aj} Nneg areusedtoestimate (cid:101) j=1
the intractable normalization constant Z(o,θ). In practice,
the inaccuracy of negative sampling is known to cause
training instability for EBMs Du et al. (2020); Ta et al.
(2022).
Diffusion Policy and DDPMs sidestep the issue of
estimating Z(a,θ) altogether by modeling the score
function Song and Ermon (2019) of the same action
distributioninEq6:
∇ logp(a|o)=−∇ E (a,o)−∇ logZ(o,θ)≈−ε (a,o)
a a θ a θ
(cid:124) (cid:123)(cid:122) (cid:125)
=0
(8)
where the noise-prediction network ε (a,o) is approximat-
θ
ing the negative of the score function ∇ logp(a|o) Liu
a
et al. (2022), which is independent of the normalization
constant Z(o,θ). As a result, neither the inference (Eq 4)
nor training (Eq 5) process of Diffusion Policy involves
evaluating Z(o,θ), thus making Diffusion Policy training
morestable.
     
     
     
     
   
          
 ) T S G L
 ) 7 1  H I V 4  R S M X G %  R M E V 8
 6 I E P  4 Y W L 8  - Q K
   
   
   
   
   
   
          
 ) T S G L
 I X E 6  W W I G G Y 7
In particular, when the prediction horizon is one time
step, T =1, it can be seen that the optimal denoiser which
p
minimizes
L =MSE(εk,ε (s,−Ks +εk,k)) (9)
θ t t
isgivenby
1
ε (s,a,k)= [a+Ks], θ σ
k
where σ is the variance on denoising iteration k.
k
Furthermore, at inference time, the DDIM sampling will
convergetotheglobalminimaata=−Ks.
Trajectory prediction (T >1) follows naturally. In order
p
topredicta t+t′ asafunctionofs t ,theoptimaldenoiserwill
producea t+t′
=−K(A−BK)t′
s t ;alltermsinvolvingw t are
zero in expectation. This shows that in order to perfectly
clone a behavior that depends on the state, the learner
must implicitly learn a (task-relevant) dynamics model
Subramanian and Mahajan (2019); Zhang et al. (2020).
Note that if either the plant or the policy is nonlinear, then
predicting future actions could become significantly more
challengingandonceagaininvolvemultimodalpredictions.
5 Evaluation
We systematically evaluate Diffusion Policy on 15 tasks
from 4 benchmarks Florence et al. (2021); Gupta et al.
(2019); Mandlekar et al. (2021); Shafiullah et al. (2022).
 7 M Q  4 Y W L 8  7 X E X I This evaluation suite includes both simulated and real
environments, single and multiple task benchmarks, fully
actuated and under-actuated systems, and rigid and
fluid objects. We found Diffusion Policy to consistently
outperform the prior state-of-the-art on all of the tested
benchmarks, with an average success-rate improvement of
46.9%.Inthefollowingsections,weprovideanoverviewof
eachtask,ourevaluationmethodologyonthattask,andour
keytakeaways.
 ( M J J Y W M S R  4 S P M G ]  - & '
5.1 Simulation Environments and datasets
Figure6. TrainingStability.Left:IBCfailstoinfertraining
Robomimic Mandlekar et al. (2021) is a large-scale
actionswithincreasingaccuracydespitesmoothlydecreasing
traininglossforenergyfunction.Right:IBC’sevaluationsuccess roboticmanipulationbenchmarkdesignedtostudyimitation
rateoscillates,makingcheckpointselectiondifficult(evaluated learning and offline RL. The benchmark consists of 5 tasks
usingpolicyrolloutsinsimulation). with a proficient human (PH) teleoperated demonstration
dataset for each and mixed proficient/non-proficient human
(MH) demonstration datasets for 4 of the tasks (9 variants
4.5 Connections to Control Theory in total). For each variant, we report results for both state-
and image-based observations. Properties for each task are
Diffusion Policy has a simple limiting behavior when the
summarizedinTab3.
tasks are very simple; this potentially allows us to bring
Push-TadaptedfromIBCFlorenceetal.(2021),requires
to bear some rigorous understanding from control theory.
pushing a T-shaped block (gray) to a fixed target (red)
Considerthecasewherewehavealineardynamicalsystem,
with a circular end-effector (blue)s. Variation is added by
instandardstate-spaceform,thatwewishtocontrol:
random initial conditions for T block and end-effector. The
s =As +Ba +w, w ∼N (0,Σ ). task requires exploiting complex and contact-rich object
t+1 t t t t w
dynamicstopushtheTblockprecisely,usingpointcontacts.
Now imagine we obtain demonstrations (rollouts) from a There are two variants: one with RGB image observations
linear feedback policy: a = −Ks. This policy could be andanotherwith92Dkeypointsobtainedfromtheground-
t t
obtained, for instance, by solving a linear optimal control truthposeoftheTblock,bothwithproprioceptionforend-
problem like the Linear Quadratic Regulator. Imitating this effectorlocation.
policy does not need the modeling power of diffusion, but MultimodalBlockPushingadaptedfromBETShafiullah
asasanitycheck,wecanseethatDiffusionPolicydoesthe et al. (2022), this task tests the policy’s ability to model
rightthing. multimodal action distributions by pushing two blocks

--- Page 7 ---
DiffusionPolicy 7
Lift Can Square Transport ToolHang Push-T
ph mh ph mh ph mh ph mh ph ph
LSTM-GMM 1.00/0.96 1.00/0.93 1.00/0.91 1.00/0.81 0.95/0.73 0.86/0.59 0.76/0.47 0.62/0.20 0.67/0.31 0.67/0.61
IBC 0.79/0.41 0.15/0.02 0.00/0.00 0.01/0.01 0.00/0.00 0.00/0.00 0.00/0.00 0.00/0.00 0.00/0.00 0.90/0.84
BET 1.00/0.96 1.00/0.99 1.00/0.89 1.00/0.90 0.76/0.52 0.68/0.43 0.38/0.14 0.21/0.06 0.58/0.20 0.79/0.70
DiffusionPolicy-C 1.00/0.98 1.00/0.97 1.00/0.96 1.00/0.96 1.00/0.93 0.97/0.82 0.94/0.82 0.68/0.46 0.50/0.30 0.95/0.91
DiffusionPolicy-T 1.00/1.00 1.00/1.00 1.00/1.00 1.00/0.94 1.00/0.89 0.95/0.81 1.00/0.84 0.62/0.35 1.00/0.87 0.95/0.79
Table1. BehaviorCloningBenchmark(StatePolicy) Wepresentsuccessrateswithdifferentcheckpointselectionmethodsin
theformatof(maxperformance)/(averageoflast10checkpoints),witheachaveragedacross3trainingseedsand50different
environmentinitialconditions(150intotal).LSTM-GMMcorrespondstoBC-RNNinRoboMimicMandlekaretal.(2021),whichwe
reproducedandobtainedslightlybetterresultsthantheoriginalpaper.OurresultsshowthatDiffusionPolicysignificantlyimproves
state-of-the-artperformanceacrosstheboard.
Lift Can Square Transport ToolHang Push-T
ph mh ph mh ph mh ph mh ph ph
LSTM-GMM 1.00/0.96 1.00/0.95 1.00/0.88 0.98/0.90 0.82/0.59 0.64/0.38 0.88/0.62 0.44/0.24 0.68/0.49 0.69/0.54
IBC 0.94/0.73 0.39/0.05 0.08/0.01 0.00/0.00 0.03/0.00 0.00/0.00 0.00/0.00 0.00/0.00 0.00/0.00 0.75/0.64
DiffusionPolicy-C 1.00/1.00 1.00/1.00 1.00/0.97 1.00/0.96 0.98/0.92 0.98/0.84 1.00/0.93 0.89/0.69 0.95/0.73 0.91/0.84
DiffusionPolicy-T 1.00/1.00 1.00/0.99 1.00/0.98 1.00/0.98 1.00/0.90 0.94/0.80 0.98/0.81 0.73/0.50 0.76/0.47 0.78/0.66
Table2. BehaviorCloningBenchmark(VisualPolicy) PerformancearereportedinthesameformatasinTab1.LSTM-GMM
numberswerereproducedtogetacompleteevaluationinadditiontothebestcheckpointperformancereported.DiffusionPolicy
showsconsistentperformanceimprovement,especiallyforcomplextaskslikeTransportandToolHang.
Task #Rob #Obj ActD #PH #MH Steps Img? HiPrec be modeled by a single function mapping from observation
toaction.
SimulationBenchmark
Franka Kitchen is a popular environment for evaluating
Lift 1 1 7 200 300 400 Yes No
the ability of IL and Offline-RL methods to learn multiple
Can 1 1 7 200 300 400 Yes No
long-horizon tasks. Proposed in Relay Policy Learning
Square 1 1 7 200 300 400 Yes Yes
Gupta et al. (2019), the Franka Kitchen environment
Transport 2 3 14 200 300 700 Yes No
ToolHang 1 2 7 200 0 700 Yes Yes contains 7 objects for interaction and comes with a
human demonstration dataset of 566 demonstrations, each
Push-T 1 1 2 200 0 300 Yes Yes
completing 4 tasks in arbitrary order. The goal is to
BlockPush 1 2 2 0 0 350 No No execute as many demonstrated tasks as possible, regardless
Kitchen 1 7 9 656 0 280 No No of order, showcasing both short-horizon and long-horizon
multimodality.
RealworldBenchmark
Push-T 1 1 2 136 0 600 Yes Yes
5.2 Evaluation Methodology
6DoFPour 1 liquid 6 90 0 600 Yes No
PeriSpread 1 liquid 6 90 0 600 Yes No
We present the best-performing for each baseline
MugFlip 1 1 7 250 0 600 Yes No
method on each benchmark from all possible sources –
Table3. TasksSummary.#Rob:numberofrobots,#Obj: our reproduced result (LSTM-GMM) or original number
numberofobjects,ActD:actiondimension,PH:
reportedinthepaper(BET,IBC).Wereportresultsfromthe
proficient-humandemonstration,MH:multi-human
average of the last 10 checkpoints (saved every 50 epochs)
demonstration,Steps:maxnumberofrolloutsteps,HiPrec:
across 3 training seeds and 50 environment initializations
whetherthetaskhasahighprecisionrequirement.BlockPush
uses1000episodesofscripteddemonstrations. * (an average of 1500 experiments in total). The metric for
mosttasksissuccessrate,exceptforthePush-Ttask,which
into two squares in any order. The demonstration data is usestargetareacoverage.Inaddition,wereporttheaverage
generated by a scripted oracle with access to groundtruth
state info. This oracle randomly selects an initial block
to push and moves it to a randomly selected square. The
∗Duetoabuginourevaluationcode,only22environmentinitializations
remaining block is then pushed into the remaining square.
areusedforrobomimictasks.Thisdoesnotchangeourconclusionsinceall
This task contains long-horizon multimodality that can not baselinemethodsareevaluatedinthesameway.

--- Page 8 ---
8
control as the diffusion-policy action space significantly
outperformed velocity control. The baseline methods we
evaluate,however,workbestwithvelocitycontrol(andthis
isreflectedintheliteraturewheremostexistingworkreports
usingvelocity-controlactionspacesMandlekaretal.(2021);
Shafiullah et al. (2022); Zhang et al. (2018); Florence et al.
(2019);Mandlekaretal.(2020b,a)).
The tradeoff in action horizon. As discussed in Sec
4.3, having an action horizon greater than 1 helps the
BlockPush Kitchen
policy predict consistent actions and compensate for idle
p1 p2 p1 p2 p3 p4
portionsofthedemonstration,buttoolongahorizonreduces
LSTM-GMM 0.03 0.01 1.00 0.90 0.74 0.34 performance due to slow reaction time. Our experiment
IBC 0.01 0.00 0.99 0.87 0.61 0.24 confirms this trade-off (Fig. 5 left) and found the action
BET 0.96 0.71 0.99 0.93 0.71 0.44 horizonof8stepstobeoptimalformosttasksthatwetested.
DiffusionPolicy-C 0.36 0.11 1.00 1.00 1.00 0.99
Robustness against latency. Diffusion Policy employs
DiffusionPolicy-T 0.99 0.94 1.00 0.99 0.99 0.96
receding horizon position control to predict a sequence
Table4. Multi-StageTasks(StateObservation).For of actions into the future. This design helps address the
PushBlock, pxisthefrequencyofpushingxblocksintothe
latency gap caused by image processing, policy inference,
targets.ForKitchen, pxisthefrequencyofinteractingwithxor
and network delay. Our ablation study with simulated
moreobjects(e.g.bottomburner).DiffusionPolicyperforms
latency showed Diffusion Policy is able to maintain peak
better,especiallyfordifficultmetricssuchas p2forBlock
Pushingand p4forKitchen,asdemonstratedbyourresults. performancewithlatencyupto4steps(Fig5).Wealsofind
thatvelocitycontrolismoreaffectedbylatencythanposition
of best-performing checkpoints for robomimic and Push- control,likelyduetocompoundingerroreffects.
T tasks to be consistent with the evaluation methodology Diffusion Policy is stable to train. We found that the
of their respective original papers Mandlekar et al. (2021); optimal hyperparameters for Diffusion Policy are mostly
Florence et al. (2021). All state-based tasks are trained for consistent across tasks. In contrast, IBC Florence et al.
4500 epochs, and image-based tasks for 3000 epochs. Each (2021) is prone to training instability. This property is
method is evaluated with its best-performing action space: discussedinSec4.4.
position control for Diffusion Policy and velocity control
for baselines (the effect of action space will be discussed
in detail in Sec 5.3). The results from these simulation
5.4 Ablation Study
benchmarksaresummarizedinTable1andTable2.
We explore alternative vision encoder design decisions
5.3 Key Findings on the simulated robomimic square task. Specifically, we
DiffusionPolicyoutperformsalternativemethodsonalltasks evaluated 3 different architectures: ResNet-18, ResNet-34
and variants, with both state and vision observations, in He et al. (2016) and ViT-B/16 Dosovitskiy et al. (2020).
our simulation benchmark study (Tabs 1, 2 and 4) with an For each architecture, we evaluated 3 different training
average improvement of 46.9%. The following paragraphs strategies: training end-to-end from scratch, using frozen
summarizethekeytakeaways. pre-trainedvisionencoder,andfinetuningpre-trainedvision
encoders (with 10x lower learning rate with respect to the
Diffusion Policy can express short-horizon multi-
policynetwork).WeuseImageNet-21kRidniketal.(2021)
modality. We define short-horizon action multimodality as
pretraining for ResNet and CLIP Radford et al. (2021)
multiplewaysofachievingthesameimmediategoal,which
pretraining for ViT-B/16. The quantitative comparison on
is prevalent in human demonstration data Mandlekar et al.
square task with proficient-human (PH) dataset is shown in
(2021).InFig3,wepresentacasestudyofthistypeofshort-
Tab.5.
horizon multimodality in the Push-T task. Diffusion Policy
learnstoapproachthecontactpointequallylikelyfromleft We found training ViT from scratch to be challenging
or right, while LSTM-GMM Mandlekar et al. (2021) and (with only 22% success rate), likely due to the limited
IBCFlorence etal.(2021)exhibit biastowardone sideand amount data. We also found training with frozen pretrained
BETShafiullahetal.(2022)cannotcommittoonemode. vision encoder to yield poor performance, which indicates
DiffusionPolicycanexpresslong-horizonmultimodal- that diffusion policy prefers different vision representation
ity.Long-horizonmultimodalityisthecompletionofdiffer- than what is offered in popular pretraining methods.
entsub-goalsininconsistentorder.Forexample,theorderof However,wefoundfinetuningthepretrainedvisionencoder
pushingaparticularblockintheBlockPushtaskortheorder with a small learning rate (10x smaller vs diffusion
ofinteractingwith7possibleobjectsintheKitchentaskare policy network) gives the best performance overall. This
arbitrary.WefindthatDiffusionPolicycopeswellwiththis is especially true for the CLIP-trained ViT-B/16, which
typeofmultimodality;itoutperformsbaselinesonbothtasks reaches 98% success rate with only 50 epochs of training.
by a large margin: 32% improvement on Block Push’s p2 Overall, the best performance across different architectures
metricand213%improvementonKitchen’sp4metric. isnotlarge,despitetheirsignificanttheoreticalcapacitygap.
Diffusion Policy can better leverage position control. We anticipate that their performance gap could be more
Our ablation study (Fig. 4) shows that selecting position pronouncedonacomplextask.

--- Page 9 ---
DiffusionPolicy 9
Archicture& From Pretrained measuredatthelaststepinsteadoftakingthemaximumover
PrertainDatset Scatch frozen finetuning allsteps.Wethresholdsuccessratebytheminimumachieved
IoUmetricfromthehumandemonstrationdataset.OurUR5-
Resnet18(in21) 0.94 0.58 0.92
based experiment setup is shown in Fig 6. Diffusion Policy
Resnet34(in21) 0.92 0.40 0.94
predictsrobotcommandsat10Hzandthesecommandsthen
ViT-base(clip) 0.22 0.70 0.98
linearlyinterpolatedto125Hzforrobotexecution.
Table5. VisionEncoderComparisonAllmodelsaretrained Result Analysis. Diffusion Policy performed close to
ontherobomimicsquare(ph)taskusingCNN-baseddiffusion human level with 95% success rate and 0.8 v.s. 0.84
policy.Eachmodelistrainedfor500epochsandevaluated
average IoU, compared with the 0% and 20% success rate
every50epochsunder50differentenvironmentinitial
of best-performing IBC and LSTM-GMM variants. Fig 7
conditions.
qualitativelyillustratesthebehaviorforeachmethodstarting
from the same initial condition. We observed that poor
performance during the transition between stages is the
② most common failure case for the baseline method due to
highmultimodalityduringthosesectionsandanambiguous
①
decisionboundary.LSTM-GMMgotstuckneartheTblock
in8outof20evaluations(3rdrow),whileIBCprematurely
left the T block in 6 out of 20 evaluations (4th row).
We did not follow the common practice of removing idle
actions from training data due to task requirements, which
also contributed to LSTM and IBC’s tendency to overfit on
smallactionsandgetstuckinthistask.Theresultsarebest
appreciatedwithvideosinsupplementalmaterials.
End-to-end v.s. pre-trained vision encoders We tested
Human IBC LSTM-GMM DiffusionPolicy DiffusionPolicywithpre-trainedvisionencoders(ImageNet
Demo pos vel pos vel T-E2EImgNetR3ME2E Deng et al. (2009) and R3MNair et al. (2022)), as seen in
IoU 0.84 0.140.190.24 0.25 0.53 0.24 0.66 0.80 Tab.6.DiffusionPolicywithR3Machievesan80%success
Succ% 1.00 0.000.000.20 0.10 0.65 0.15 0.80 0.95 ratebutpredictsjitteryactionsandismorelikelytogetstuck
Dur. 20.3 56.341.647.3 51.7 57.5 55.8 31.7 22.9 comparedtotheend-to-endtrainedversion.DiffusionPolicy
Table6. RealworldPush-TExperiment.a)Hardwaresetup. with ImageNet showed less promising results with abrupt
b)Illustrationofthetask.Therobotneedsto⃝1 preciselypush actions and poor performance. We found that end-to-end
theT-shapedblockintothetargetregion,and⃝2 movethe training is still the most effective way to incorporate visual
end-effectortotheend-zone.c)Thegroundtruthendstate observation into Diffusion Policy, and our best-performing
usedtocalculateIoUmetricsusedinthistable.Table:Success
modelswereallend-to-endtrained.
isdefinedbytheend-stateIoUgreaterthantheminimumIoUin
Robustness against perturbation Diffusion Policy’s
thedemonstrationdataset.Averageepisodedurationpresented
robustness against visual and physical perturbations was
inseconds.T-E2Estandsforend-to-endtrained
Transformer-basedDiffusionPolicy evaluated in a separate episode from experiments in Tab
6. As shown in Fig 8, three types of perturbations are
6 Realworld Evaluation applied. 1) The front camera was blocked for 3 secs by a
waving hand (left column), but the diffusion policy, despite
WeevaluatedDiffusionPolicyintherealworldperformance
exhibiting some jitter, remained on-course and pushed the
on4tasksacross2hardwaresetups–withtrainingdatafrom
T block into position. 2) We shifted the T block while
different demonstrators for each setup. On the realworld
Diffusion Policy was making fine adjustments to the T
Push-T task, we perform ablations examining Diffusion
block’s position. Diffusion policy immediately re-planned
Policyon2architectureoptionsand3visualencoderoptions;
to push from the opposite direction, negating the impact of
we also benchmarked against 2 baseline methods with
perturbation. 3) We moved the T block while the robot was
both position-control and velocity-control action spaces.
en route to the end-zone after the first stage’s completion.
On all tasks, Diffusion Policy variants with both CNN
The Diffusion Policy immediately changed course to adjust
backbones and end-to-end-trained visual encoders yielded
theTblockbacktoitstargetandthencontinuedtotheend-
thebestperformance.Moredetailsaboutthetasksetupand
zone. This experiment indicates that Diffusion Policy may
parametersmaybefoundinsupplementalmaterials.
beabletosynthesizenovelbehaviorinresponsetounseen
observations.
6.1 Realworld Push-T Task
6.2 Mug Flipping Task
Real-worldPush-Tissignificantlyharderthanthesimulated
version due to 3 modifications: 1. The real-world Push-T ThemugflippingtaskisdesignedtotestDiffusionPolicy’s
task is multi-stage. It requires the robot to ⃝1 push the abilitytohandlecomplex3Drotationswhileoperatingclose
T block into the target and then ⃝2 move its end-effector to the hardware’s kinematic limits. The goal is to reorient a
intoadesignatedend-zonetoavoidocclusion.2.Thepolicy randomlyplacedmugtohave⃝1 thelipfacingdown⃝2 the
needs to make fine adjustments to make sure the T is fully handle pointing left, as shown in Fig. 9. Depending on the
in the goal region before heading to the end-zone, creating mug’sinitialpose,thedemonstratormightdirectlyplacethe
additional short-term multimodality. 3. The IoU metric is mugindesiredorientation,ormayuseadditionalpushofthe

--- Page 10 ---
10
Time Avg of End States
Diffusion
Policy
(End2End)
A
Diffusion
Policy
(R3M)
B
LSTM-GMM
(End2End)
C
IBC
(End2End)
D
Figure7. RealworldPush-TComparisons.Columns1-4showactiontrajectoriesbasedonkeyevents.Thelastcolumnshows
averagedimagesoftheendstate.A:Diffusionpolicy(End2End)achievesmoreaccurateandconsistentendstates.B:Diffusion
Policy(R3M)getsstuckinitiallybutlaterrecoversandfinishesthetask.C:LSTM-GMMfailstoreachtheendzonewhileadjusting
theTblock,blockingtheevalcameraview.D:IBCprematurelyendsthepushingstage.
Visual Perturbation during Perturbation during
Occlusion Pushing Stage Finishing Stage
1
2
Human LSTM-GMM DiffusionPolicy
Figure8. RobustnessTestforDiffusionPolicy.Left:A
wavinghandinfrontofthecamerafor3secondscausesslight Succ% 1.0 0.0 0.9
jitter,butthepredictedactionsstillfunctionasexpected.
Middle:DiffusionPolicyimmediatelycorrectsshiftedblock Figure9. 6DoFMugFlippingTask.Therobotneedsto⃝1
positiontothegoalstateduringthepushingstage.Right:Policy Pickuparandomlyplacedmugandplaceitlipdown(marked
immediatelyabortsheadingtotheendzone,returningtheblock orange).⃝2 Rotatethemugsuchthatitshandleispointingleft.
togoalstateupondetectingblockshift.Thisnovelbehaviorwas
neverdemonstrated.Pleasecheckthevideosinthe
supplementarymaterial. 6.3 Sauce Pouring and Spreading
handle to rotation the mug. As a result, the demonstration The sauce pouring and spreading tasks are designed to test
datasetishighlymulti-modal:graspvspush,differenttypes DiffusionPolicy’sabilitytoworkwithnon-rigidobjects,6
ofgrasps(forehandvsbackhand)orlocalgraspadjustments Dofactionspaces,andperiodicactionsinreal-worldsetups.
(rotation around mug’s principle axis), and are particularly OurFrankaPandasetupandtasksareshowninFig10.The
challengingforbaselineapproachestocapture. goal for the 6DoF pouring task is to pour one full ladle of
Result Analysis. Diffusion policy is able to complete sauce onto the center of the pizza dough, with performance
this task with 90% success rate over 20 trials. The richness measured by IoU between the poured sauce mask and a
of captured behaviors is best appreciated with the video. nominal circle at the center of the pizza dough (illustrated
Although never demonstrated, the policy is also able to by the green circle in Fig 10). The goal for the periodic
sequence multiple pushes for handle alignment or regrasps spreading task is to spread sauce on pizza dough, with
for dropped mug when necessary. For comparison, we also performancemeasuredbysaucecoverage.Variationsacross
trainaLSTM-GMMpolicytrainedwithasubsetofthesame evaluation episodes come from random locations for the
data. For 20 in-distribution initial conditions, the LSTM- doughandthesaucebowl.Thesuccessrateiscomputedby
GMMpolicyneveralignsproperlywithrespecttothemug, thresholdingwithminimumhumanperformance.Resultsare
andfailstograspinalltrials. bestviewedinsupplementalvideos.Bothtasksweretrained

--- Page 11 ---
DiffusionPolicy 11
Spreading Goal 7 Realworld Bimanual Tasks
Beyond single arm setup, we further demonstrate Diffusion
Policy on several challenging bimanual tasks. To enable
bimanualtasks,themajorityofeffortwasspentonextending
ourrobotstacktosupportmulti-armteleoprationandcontrol.
Diffusion Policy worked out of the box for these tasks
1
Pouring Goal 4 withouthyperparametertuning.
3
2 1
3 7.1 Observation and Action Spaces
2
Theproprioceptiveobservationspaceisextendedtoinclude
Pour Spread theposesofbothend-effectorsandthegripperwidthsofboth
IoU Succ Coverage Succ% grippers. We also extend the observation space to include
theactualanddesiredvaluesofthesequantities.Theimage
Human 0.79 1.00 0.79 1.00
observation space is comprised of two scene cameras and
LSTM-GMM 0.06 0.00 0.27 0.00
two wrist cameras, one attached to each arm. The action
DiffusionPolicy 0.74 0.79 0.77 1.00
space is extended to include the desired poses of both end-
effectorsandthedesiredgripperwidthsofbothgrippers.
Figure10. RealworldSauceManipulation. [Left]6DoF
pouringTask.Therobotneedsto⃝1 diptheladletoscoop
saucefromthebowl,⃝2 approachthecenterofthepizza 7.2 Teleoperation
dough,⃝3 poursauce,and⃝4 lifttheladletofinishthetask.
For these coordinated bimanual tasks, we found using
[Right]PeriodicspreadingTaskTherobotneedsto⃝1
2 SpaceMouse simultaneously quite challenging for the
approachthecenterofthesaucewithagraspedspoon,⃝2
spreadthesaucetocoverpizzainaspiralpattern,and⃝3 lift demonstrator.Thus,weimplementedtwonewteleoperation
thespoontofinishthetask. modes: using a Meta Quest Pro VR device with two
hand controllers, or haptic-enabled control using 2 Haption
with the same Push-T hyperparameters, and successful Virtuose™ 6D HF TAO devices using bilateral position-
policieswereachievedonthefirstattempt. position coupling as described succinctly in the haptics
The sauce pouring task requires the robot to remain sectionofSicilianoetal.(2008).Thiscouplingisperformed
stationary for a period of time to fill the ladle with viscous between a Haption device and a Franka Panda arm. More
tomato sauce. The resulting idle actions are known to be details on the controllers themselves may be found in Sec.
challenging for behavior cloning algorithms and therefore D.1. The following provides more details on each task and
are often avoided or filtered out. Fine adjustments during policyperformance.
pouring are necessary during sauce pouring to ensure
coverageandtoachievethedesiredshape. 7.3 Bimanual Egg Beater
Thedemonstratedsauce-spreadingstrategyisinspiredby
The bimanual egg beater task is illustrated and described
the human chef technique, which requires both a long-
in Fig. 11, using a OXO™Egg Beater and a Room
horizon cyclic pattern to maximize coverage and short-
Essentials™plasticbowl.Wechosethistasktoillustratethe
horizon feedback for even distribution (since the tomato
importance of haptic feedback for teleoperating bimanual
sauce used often drips out in lumps with unpredictable
manipulation even for common daily life tasks such as
sizes). Periodic motions are known to be difficult to learn
coordinatedtooluse.Withouthapticfeedback,anexpertwas
and therefore are often addressed by specialized action
unable to successfully complete a single demonstration out
representations Yang et al. (2022). Both tasks require the
of 10 trials. 5 failed due to robot pulling the crank handle
policytoself-terminatebyliftingtheladle/spoon.
off the egg beater; 3 failed due to robot losing grasp of
Result Analysis. Diffusion policy achieves close-to-
the handle; 2 failed due to robot triggering torque limit. In
human performance on both tasks, with coverage 0.74 vs
contrast,thesameoperatorcouldeasilyperformthistask10
0.79 on pouring and 0.77 vs 0.79 on spreading. Diffusion
outof10timeswithhapticfeedback.Usinghapticfeedback
policy reacted gracefully to external perturbations such
made it possible for the demonstrations to be both quicker
as moving the pizza dough by hand during pouring and
andhigherqualitythanwithoutfeedback.
spreading. Results are best appreciated with videos in the
ResultAnalysis.Diffusionpolicyisabletocompletethis
supplementalmaterial.
task with 55% success rate over 20 trials, trained using
LSTM-GMMperformspoorlyonbothsaucepouringand
210 demonstrations. The primary failure modes for these
spreading tasks. It failed to lift the ladle after successfully
were out-of-domain initial positioning of the egg beater, or
scooping sauce in 15 out of 20 of the pouring trials. When
missingtheeggbeatercrankhandleorlosinggraspofit.The
the ladle was successfully lifted, the sauce was poured
initialandfinalstatesforallrolloutsarevisualizedin18and
off-centered. LSTM-GMM failed to self-terminate in all
19.
trials. We suspect LSTM-GMM’s hidden state failed to
capture sufficiently long history to distinguish between the
7.4 Bimanual Mat Unrolling
ladle dipping and the lifting phases of the task. For sauce
spreading, LSTM-GMM always lifts the spoon right after The mat unrolling task is shown and described in Fig.
thestart,andfailedtomakecontactwiththesauceinall20 12, using a XXL Dog Buddy™Dog Mat. This task was
experiments. teleoperated using the VR setup, as it did not require rich

--- Page 12 ---
12
4
3
5
2
1
Figure11. BimanualEggBeaterManipulation. Therobot
needsto⃝1 pushthebowlintoposition(onlyiftooclosetothe
leftarm),⃝2 approachandpickuptheeggbeaterwiththeright
arm,⃝3 placetheeggbeaterinthebowl,⃝4 approachand
grasptheeggbeatercrankhandle,and⃝5 turnthecrank
handle3ormoretimes.
1
3
Figure13. BimanualShirtFolding. Therobotneedsto⃝1
5 6 approachandgrasptheclosestsleevewithbotharms,⃝2 fold
4
2 thesleeveandrelease,⃝3 dragtheshirtcloser(ifneeded),⃝4
approachandgrasptheothersleevewithbotharms,⃝5 foldthe
sleeveandrelease,⃝6 dragtheshirttoaorientationforfolding,
Figure12. BimanualMatUnrolling. Therobotneedsto⃝1 ⃝7 graspandfoldtheshirtinhalfbyitscollar,⃝8 dragtheshirt
pickuponesideofthemat(ifneeded),usingtheleftorright tothecenter,and⃝9 smoothouttheshirtandmovethearms
arm,⃝2 liftandunrollthemat(ifneeded),⃝3 ensurethatboth away.
sidesofthemataregrasped,⃝4 liftthemat,⃝5 placethemat
orientedwiththetable,mostlycentered,and⃝6 releasethemat. et al. (2020). While conceptually simple, behavior cloning
has shown surprising promise on an array of real-world
haptic feedback to perform the task. We taught this skill to robot tasks, including manipulation Zhang et al. (2018);
be omnidextrous, meaning it can unroll either to the left or Florence et al. (2019); Mandlekar et al. (2020b,a); Zeng
rightdependingontheinitialcondition. etal.(2021);Rahmatizadehetal.(2018);Avigaletal.(2022)
ResultAnalysis.Diffusionpolicyisabletocompletethis and autonomous driving Pomerleau (1988); Bojarski et al.
taskwith75%successrateover20trials,trainedusing162 (2016).Currentbehaviorcloningapproachescanbecatego-
demonstrations. The primary failure modes for these were rizedintotwogroups,dependingonthepolicy’sstructure.
missed grasps during initial grasp of the mat, where the Explicit Policy. The simplest form of explicit policies
policystruggledtocorrectitselfandthusgotstuckrepeating maps from world state or observation directly to action
thesamebehavior.Theinitialandfinalstatesforallrollouts Pomerleau (1988); Zhang et al. (2018); Florence et al.
arevisualizedin16and17. (2019);Rossetal.(2011);Toyeretal.(2020);Rahmatizadeh
et al. (2018); Bojarski et al. (2016). They can be
7.5 Bimanual Shirt Folding. supervised with a direct regression loss and have efficient
TheshirtfoldingtaskisdescribedandillustratedinFig.13, inference time with one forward pass. Unfortunately, this
using a short-sleeve T-shirt. This task was also teleoperated type of policy is not suitable for modeling multi-modal
using the VR setup as it did not require rich feedback demonstrated behavior, and struggles with high-precision
to perform the task. Due to the kinematic and workspace tasks Florence et al. (2021). A popular approach to
constraints, this task is notably longer and can take up model multimodal action distributions while maintaining
to nine discrete steps. The last few steps require both the simplicity of direction action mapping is convert
gripperstocomeveryclosetowardseachother.Havingour the regression task into classification by discretizing the
mid-level controller explicitly handling collision avoidance action space Zeng et al. (2021); Wu et al. (2020); Avigal
was especially important for both teleoperation and policy et al. (2022). However, the number of bins needed to
rollout. approximate acontinuous actionspace growsexponentially
ResultAnalysis.Diffusionpolicyisabletocompletethis with increasing dimensionality. Another approach is to
taskwith75%successrateover20trials,trainedusing284 combineCategoricalandGaussiandistributionstorepresent
demonstrations. The primary failure modes for these were continuous multimodal distributions via the use of MDNs
missed grasps for initial folding (the sleeves and the color), Bishop (1994); Mandlekar et al. (2021) or clustering with
andthepolicybeingunabletostopadjustingtheshirtatthe offset prediction Shafiullah et al. (2022); Sharma et al.
end.Theinitialandfinalstatesforallrolloutsarevisualized (2018). Nevertheless, these models tend to be sensitive to
in20and21. hyperparameter tuning, exhibit mode collapse, and are still
limited in their ability to express high-precision behavior
Florenceetal.(2021).
8 Related Work
Implicit Policy. Implicit policies (Florence et al. 2021;
Creatingcapablerobotswithoutrequiringexplicitprogram- Jarrettetal.2020)definedistributionsoveractionsbyusing
ming of behaviors is a longstanding challenge in the field Energy-Based Models (EBMs) (LeCun et al. 2006; Du and
AtkesonandSchaal(1997);Argalletal.(2009);Ravichandar Mordatch 2019; Dai et al. 2019; Grathwohl et al. 2020;

--- Page 13 ---
DiffusionPolicy 13
Du et al. 2020). In this setting, each action is assigned (2023); Hansen-Estruch et al. (2023), to take advantage of
an energy value, with action prediction corresponding to suboptimal and negative data. Second, diffusion policy has
the optimization problem of finding a minimal energy higher computational costs and inference latency compared
action. Since different actions may be assigned low tosimplermethodslikeLSTM-GMM.Ouractionsequence
energies, implicit policies naturally represent multi-modal prediction approach partially mitigates this issue, but may
distributions. However, existing implicit policies (Florence not suffice for tasks requiring high rate control. Future
et al. 2021) are unstable to train due to the necessity of workcanexploitthelatestadvancementsindiffusionmodel
drawing negative samples when computing the underlying acceleration methods to reduce the number of inference
Info-NCEloss. steps required, such as new noise schedules Chen (2023),
Diffusion Models. Diffusion models are probabilistic inference solvers Karras et al. (2022), and consistency
generative models that iteratively refine randomly sampled modelsSongetal.(2023).
noise into draws from an underlying distribution. They can
alsobeconceptuallyunderstoodaslearningthegradientfield
10 Conclusion
ofanimplicitactionscoreandthenoptimizingthatgradient
during inference. Diffusion models (Sohl-Dickstein et al. In this work, we assess the feasibility of diffusion-based
2015; Ho et al. 2020) have recently been applied to solve policies for robot behaviors. Through a comprehensive
various different control tasks (Janner et al. 2022a; Urain evaluation of 15 tasks in simulation and the real world,
etal.2022;Ajayetal.2022). we demonstrate that diffusion-based visuomotor policies
In particular, Janner et al. (2022a) and Huang et al. consistently and definitively outperform existing methods
(2023) explore how diffusion models may be used in the while also being stable and easy to train. Our results also
context of planning and infer a trajectory of actions that highlight critical design factors, including receding-horizon
may be executed in a given environment. In the context of actionprediction,end-effectorpositioncontrol,andefficient
Reinforcement Learning, Wang et al. (2022) use diffusion visual conditioning, that is crucial for unlocking the full
modelforpolicyrepresentationandregularizationwithstate- potential of diffusion-based policies. While many factors
based observations. In contrast, in this work, we explore affect the ultimate quality of behavior-cloned policies —
how diffusion models may instead be effectively applied in including the quality and quantity of demonstrations, the
the context of behavioral cloning for effective visuomotor physical capabilities of the robot, the policy architecture,
control policy. To construct effective visuomotor control andthepretrainingregimeused—ourexperimentalresults
policies, we propose to combine DDPM’s ability to predict strongly indicate that policy structure poses a significant
high-dimensional action squences with closed-loop control, performance bottleneck during behavior cloning. We hope
aswellasanewtransformerarchitectureforactiondiffusion that this work drives further exploration in the field into
and a manner to integrate visual inputs into the action diffusion-based policies and highlights the importance of
diffusionmodel. considering all aspects of the behavior cloning process
Wangetal.(2023)explorehowdiffusionmodelslearned beyondjustthedatausedforpolicytraining.
from expert demonstrations can be used to augment
classical explicit polices without directly taking advantage 11 Acknowledgement
ofdiffusionmodelsaspolicyrepresentation.
We’d like to thank Naveen Kuppuswamy, Hongkai Dai,
Concurrent to us, Pearce et al. (2023), Reuss et al.
Aykut O¨nol, Terry Suh, Tao Pang, Huy Ha, Samir Gadre,
(2023) and Hansen-Estruch et al. (2023) has conducted
Kevin Zakka and Brandon Amos for their thoughtful
a complimentary analysis of diffusion-based policies in
discussions.WethankJarodWilsonfor3Dprintingsupport
simulatedenvironments.Whiletheyfocusmoreoneffective
andHuyHaforphotographyandlightingadvice.Wethank
sampling strategies, leveraging classifier-free guidance for
Xiang Li for discovering the bug in our evaluation code on
goal-conditioning as well as applications in Reinforcement
GitHub.
Learning, and we focus on effective action spaces, our
empirical findings largely concur in the simulated regime.
In addition, our extensive real-world experiments provide Funding
strong evidence for the importance of a receding-horizon This work was supported by the Toyota Research Institute, NSF
prediction scheme, the careful choice between velocity and CMMI-2037101 and NSF IIS-2132519. We would like to thank
position control, and the necessity of optimization for real- Google for the UR5 robot hardware. The views and conclusions
time inference and other critical design decisions for a contained herein are those of the authors and should not be
physicalrobotsystem. interpreted as necessarily representing the official policies, either
expressedorimplied,ofthesponsors.
9 Limitations and Future Work
References
Although we have demonstrated the effectiveness of
diffusion policy in both simulation and real-world systems, Ajay A, Du Y, Gupta A, Tenenbaum J, Jaakkola T and Agrawal
there are limitations that future work can improve. First, P (2022) Is conditional generative modeling all you need for
our implementation inherits limitations from behavior decision-making? arXivpreprintarXiv:2211.15657.
cloning, such as suboptimal performance with inadequate Argall BD, Chernova S, Veloso M and Browning B (2009) A
demonstration data. Diffusion policy can be applied to survey of robot learning from demonstration. Robotics and
otherparadigms,suchasreinforcementlearningWangetal. autonomoussystems57(5):469–483.

--- Page 14 ---
14
Atkeson CG and Schaal S (1997) Robot learning from HoJ,JainAandAbbeelP(2020)Denoisingdiffusionprobabilistic
demonstration. In:ICML,volume97.pp.12–20. models. arXivpreprintarXiv:2006.11239.
AvigalY,BerscheidL,AsfourT,Kro¨gerTandGoldbergK(2022) HuangS,WangZ,LiP,JiaB,LiuT,ZhuY,LiangWandZhuSC
Speedfolding:Learningefficientbimanualfoldingofgarments. (2023)Diffusion-basedgeneration,optimization,andplanning
In: 2022 IEEE/RSJ International Conference on Intelligent in3dscenes. arXivpreprintarXiv:2301.06015.
RobotsandSystems(IROS).IEEE,pp.1–8. Janner M, Du Y, Tenenbaum J and Levine S (2022a) Planning
BishopCM(1994)Mixturedensitynetworks. AstonUniversity. withdiffusionforflexiblebehaviorsynthesis.In:International
Bojarski M, Del Testa D, Dworakowski D, Firner B, Flepp B, ConferenceonMachineLearning.
Goyal P, Jackel LD, Monfort M, Muller U, Zhang J et al. JannerM,DuY,TenenbaumJandLevineS(2022b)Planningwith
(2016)Endtoendlearningforself-drivingcars.arXivpreprint diffusion for flexible behavior synthesis. In: Chaudhuri K,
arXiv:1604.07316. Jegelka S, Song L, Szepesvari C, Niu G and Sabato S (eds.)
ChenT(2023)Ontheimportanceofnoiseschedulingfordiffusion Proceedingsofthe39thInternationalConferenceonMachine
models. arXivpreprintarXiv:2301.10972. Learning,ProceedingsofMachineLearningResearch.PMLR.
ChiC,FengS,DuY,XuZ,CousineauE,BurchfielBandSongS Jarrett D, Bica I and van der Schaar M (2020) Strictly batch
(2023)Diffusionpolicy:Visuomotorpolicylearningviaaction imitation learning by energy-based distribution matching.
diffusion. In: Proceedings of Robotics: Science and Systems AdvancesinNeuralInformationProcessingSystems33:7354–
(RSS). 7365.
DaiB,LiuZ,DaiH,HeN,GrettonA,SongLandSchuurmansD Karras T, Aittala M, Aila T and Laine S (2022) Elucidating the
(2019)Exponentialfamilyestimationviaadversarialdynamics design space of diffusion-based generative models. arXiv
embedding. Advances in Neural Information Processing preprintarXiv:2206.00364.
Systems32. KhatibO(1987)Aunifiedapproachformotionandforcecontrolof
Deng J, Dong W, Socher R, Li LJ, Li K and Fei-Fei L (2009) robotmanipulators:Theoperationalspaceformulation. IEEE
Imagenet:Alarge-scalehierarchicalimagedatabase. In:2009 Journal on Robotics and Automation 3(1): 43–53. DOI:10.
IEEEconferenceoncomputervisionandpatternrecognition. 1109/JRA.1987.1087068. ConferenceName:IEEEJournalon
Ieee,pp.248–255. RoboticsandAutomation.
Dosovitskiy A, Beyer L, Kolesnikov A, Weissenborn D, Zhai X, LeCunY,ChopraS,HadsellR,HuangFJandetal(2006)Atutorial
UnterthinerT,DehghaniM,MindererM,HeigoldG,GellyS onenergy-basedlearning.In:PredictingStructuredData.MIT
etal.(2020)Animageisworth16x16words:Transformersfor Press.
imagerecognitionatscale. arXivpreprintarXiv:2010.11929. Liu L, Liu X, Gao J, Chen W and Han J (2020) Understanding
Du Y, Li S, Tenenbaum J and Mordatch I (2020) Improved the difficulty of training transformers. arXiv preprint
contrastivedivergencetrainingofenergybasedmodels. arXiv arXiv:2004.08249.
preprintarXiv:2012.01316. Liu N, Li S, Du Y, Torralba A and Tenenbaum JB (2022)
DuYandMordatchI(2019)Implicitgenerationandgeneralization Compositional visual generation with composable diffusion
inenergy-basedmodels. arXivpreprintarXiv:1903.08689. models. arXivpreprintarXiv:2206.01714.
Florence P, Lynch C, Zeng A, Ramirez OA, Wahid A, Downs L, MandlekarA,RamosF,BootsB,SavareseS,Fei-FeiL,GargAand
Wong A, Lee J, Mordatch I and Tompson J (2021) Implicit FoxD(2020a)Iris:Implicitreinforcementwithoutinteraction
behavioral cloning. In: 5th Annual Conference on Robot at scale for learning control from offline robot manipulation
Learning. data. In:2020IEEEInternationalConferenceonRoboticsand
Florence P, Manuelli L and Tedrake R (2019) Self-supervised Automation(ICRA).IEEE.
correspondenceinvisuomotorpolicylearning. IEEERobotics Mandlekar A, Xu D, Mart´ın-Mart´ın R, Savarese S and Fei-Fei L
andAutomationLetters5(2):492–499. (2020b)Learningtogeneralizeacrosslong-horizontasksfrom
Grathwohl W, Wang KC, Jacobsen JH, Duvenaud D and Zemel humandemonstrations. arXivpreprintarXiv:2003.06085.
R (2020) Learning the stein discrepancy for training and Mandlekar A, Xu D, Wong J, Nasiriany S, Wang C, Kulkarni R,
evaluating energy-based models without sampling. In: Fei-Fei L, Savarese S, Zhu Y and Mart´ın-Mart´ın R (2021)
InternationalConferenceonMachineLearning. What matters in learning from offline human demonstrations
Gupta A, Kumar V, Lynch C, Levine S and Hausman K (2019) for robot manipulation. In: 5th Annual Conference on Robot
Relaypolicylearning:Solvinglong-horizontasksviaimitation Learning.
andreinforcementlearning.arXivpreprintarXiv:1910.11956. Mayne DQ and Michalska H (1988) Receding horizon control
Hansen-Estruch P, Kostrikov I, Janner M, Kuba JG and Levine S of nonlinear systems. In: Proceedings of the 27th IEEE
(2023)Idql:Implicitq-learningasanactor-criticmethodwith ConferenceonDecisionandControl.IEEE,pp.464–465.
diffusionpolicies. arXivpreprintarXiv:2304.10573. NairS,RajeswaranA,KumarV,FinnCandGuptaA(2022)R3m:
He K, Fan H, Wu Y, Xie S and Girshick R (2020) Momentum A universal visual representation for robot manipulation. In:
contrast for unsupervised visual representation learning. In: 6thAnnualConferenceonRobotLearning.
ProceedingsoftheIEEE/CVFconferenceoncomputervision Neal RM et al. (2011) Mcmc using hamiltonian dynamics.
andpatternrecognition.pp.9729–9738. Handbookofmarkovchainmontecarlo.
HeK,ZhangX,RenSandSunJ(2016)Deepresiduallearningfor Nichol AQ and Dhariwal P (2021) Improved denoising diffusion
imagerecognition. In:ProceedingsoftheIEEEconferenceon probabilisticmodels.In:InternationalConferenceonMachine
computervisionandpatternrecognition.pp.770–778. Learning.PMLR,pp.8162–8171.

--- Page 15 ---
DiffusionPolicy 15
PearceT,RashidT,KanervistoA,BignellD,SunM,GeorgescuR, informationprocessingsystems32.
MacuaSV,TanSZ,MomennejadI,HofmannKetal.(2023) Subramanian J and Mahajan A (2019) Approximate information
Imitating human behaviour with diffusion models. arXiv state for partially observed systems. In: 2019 IEEE 58th
preprintarXiv:2301.10677. ConferenceonDecisionandControl(CDC).IEEE,pp.1629–
PerezE,StrubF,DeVriesH,DumoulinVandCourvilleA(2018) 1636.
Film:Visualreasoningwithageneralconditioninglayer. In: Ta DN, Cousineau E, Zhao H and Feng S (2022) Conditional
ProceedingsoftheAAAIConferenceonArtificialIntelligence. energy-based models for implicit policies: The gap between
Pomerleau DA (1988) Alvinn: An autonomous land vehicle in a theoryandpractice. arXivpreprintarXiv:2207.05824.
neural network. Advances in neural information processing TancikM,SrinivasanP,MildenhallB,Fridovich-KeilS,Raghavan
systems1. N, Singhal U, Ramamoorthi R, Barron J and Ng R (2020)
Radford A, Kim JW, Hallacy C, Ramesh A, Goh G, Agarwal S, Fourier features let networks learn high frequency functions
SastryG,AskellA,MishkinP,ClarkJetal.(2021)Learning inlowdimensionaldomains. AdvancesinNeuralInformation
transferablevisualmodelsfromnaturallanguagesupervision. ProcessingSystems33:7537–7547.
In:Internationalconferenceonmachinelearning.PMLR,pp. Toyer S, Shah R, Critch A and Russell S (2020) The magical
8748–8763. benchmark for robust imitation. Advances in Neural
Rahmatizadeh R, Abolghasemi P, Bo¨lo¨ni L and Levine S (2018) InformationProcessingSystems33:18284–18295.
Vision-based multi-task manipulation for inexpensive robots Urain J, Funk N, Chalvatzaki G and Peters J (2022) Se (3)-
usingend-to-endlearningfromdemonstration. In:2018IEEE diffusionfields: Learning cost functions for joint grasp and
international conference on robotics and automation (ICRA). motion optimization through diffusion. arXiv preprint
IEEE,pp.3758–3765. arXiv:2209.03855.
Ravichandar H, Polydoros AS, Chernova S and Billard A (2020) VaswaniA,ShazeerN,ParmarN,UszkoreitJ,JonesL,GomezAN,
Recentadvancesinrobotlearningfromdemonstration.Annual Kaiser Ł and Polosukhin I (2017) Attention is all you need.
review of control, robotics, and autonomous systems 3: 297– Advancesinneuralinformationprocessingsystems30.
330. Wang Z, Hunt JJ and Zhou M (2022) Diffusion policies as an
Reuss M, Li M, Jia X and Lioutikov R (2023) Goal-conditioned expressive policy class for offline reinforcement learning.
imitation learning using score-based diffusion policies. In: arXivpreprintarXiv:2208.06193.
ProceedingsofRobotics:ScienceandSystems(RSS). Wang Z, Hunt JJ and Zhou M (2023) Diffusion policies as an
Ridnik T, Ben-Baruch E, Noy A and Zelnik-Manor L (2021) expressive policy class for offline reinforcement learning.
Imagenet-21kpretrainingforthemasses. In: The Eleventh International Conference on Learning
Ronneberger O, Fischer P and Brox T (2015) U-net: Convolu- Representations. URL https://openreview.net/
tionalnetworksforbiomedicalimagesegmentation. In:Med- forum?id=AHvFDPi-FA.
ical Image Computing and Computer-Assisted Intervention– Welling M and Teh YW (2011) Bayesian learning via stochastic
MICCAI 2015: 18th International Conference, Munich, Ger- gradient langevin dynamics. In: Proceedings of the 28th
many, October 5-9, 2015, Proceedings, Part III 18. Springer, internationalconferenceonmachinelearning(ICML-11).pp.
pp.234–241. 681–688.
RossS,GordonGandBagnellD(2011)Areductionofimitation Wu J, Sun X, Zeng A, Song S, Lee J, Rusinkiewicz S
learningandstructuredpredictiontono-regretonlinelearning. and Funkhouser T (2020) Spatial action maps for mobile
In: Proceedings of the fourteenth international conference manipulation. In: Proceedings of Robotics: Science and
on artificial intelligence and statistics. JMLR Workshop and Systems(RSS).
ConferenceProceedings,pp.627–635. WuYandHeK(2018)Groupnormalization.In:Proceedingsofthe
ShafiullahNMM,CuiZJ,AltanzayaAandPintoL(2022)Behavior Europeanconferenceoncomputervision(ECCV).pp.3–19.
transformers:Cloning$k$modeswithonestone. In:OhAH, YangJ,ZhangJ,SettleC,RaiA,AntonovaRandBohgJ(2022)
AgarwalA,BelgraveDandChoK(eds.)AdvancesinNeural Learningperiodictasksfromhumandemonstrations. In:2022
InformationProcessingSystems. InternationalConferenceonRoboticsandAutomation(ICRA).
Sharma P, Mohan L, Pinto L and Gupta A (2018) Multiple IEEE,pp.8658–8665.
interactions made easy (mime): Large scale demonstrations Zeng A, Florence P, Tompson J, Welker S, Chien J, Attarian M,
dataforimitation. In:Conferenceonrobotlearning.PMLR. Armstrong T, Krasin I, Duong D, Sindhwani V et al. (2021)
SicilianoB,KhatibOandKro¨gerT(2008)Springerhandbookof Transporternetworks:Rearrangingthevisualworldforrobotic
robotics,volume200. Springer. manipulation. In:ConferenceonRobotLearning.PMLR,pp.
Sohl-Dickstein J, Weiss E, Maheswaranathan N and Ganguli 726–747.
S (2015) Deep unsupervised learning using nonequilibrium Zhang A, McAllister RT, Calandra R, Gal Y and Levine S
thermodynamics. In: International Conference on Machine (2020) Learning invariant representations for reinforcement
Learning. learningwithoutreconstruction. In:InternationalConference
Song J, Meng C and Ermon S (2021) Denoising diffusion onLearningRepresentations.
implicit models. In: International Conference on Learning Zhang T, McCarthy Z, Jow O, Lee D, Chen X, Goldberg K
Representations. and Abbeel P (2018) Deep imitation learning for complex
SongY,DhariwalP,ChenMandSutskeverI(2023)Consistency manipulationtasksfromvirtualrealityteleoperation. In:2018
models. arXivpreprintarXiv:2303.01469. IEEE International Conference on Robotics and Automation
Song Y and Ermon S (2019) Generative modeling by estimating (ICRA).IEEE,pp.5628–5635.
gradients of the data distribution. Advances in neural

--- Page 16 ---
16
ZhouY,BarnesC,LuJ,YangJandLiH(2019)Onthecontinuity
ofrotationrepresentationsinneuralnetworks. In:Proceedings    
oftheIEEE/CVFConferenceonComputerVisionandPattern
   
Recognition.pp.5745–5753.
   
   
A Diffusion Policy Implementation Details
               
A.1 Normalization
Properly normalizing action data is critical to achieve best
performance for Diffusion Policy. Scaling the min and max
ofeachactiondimensionindependentlyto[−1,1]workswell
for most tasks. Since DDPMs clip prediction to [−1,1] at
each iteration to ensure stability, the common zero-mean
unit-variance normalization will cause some region of the
action space to be inaccessible. When the data variance is
small(e.g.,nearconstantvalue),shiftthedatatozero-mean
withoutscalingtopreventnumericalissues.Weleaveaction
dimensions corresponding to rotation representations (e.g.
Quaternion)unchanged.
A.2 Rotation Representation
For all environments with velocity control action space, we
followedthestandardpracticeMandlekaretal.(2021)touse
3D axis-angle representation for the rotation component of
action. Since velocity action commands are usually close
to 0, the singularity and discontinuity of the axis-angle
representation don’t usually cause problems. We used the
6DrotationrepresentationproposedinZhouetal.(2019)for
allenvironments(real-worldandsimulation)withpositional
controlactionspace.
A.3 Image Augmentation
Following Mandlekar et al. (2021), we employed random
crop augmentation during training. The crop size for each
taskisindicatedinTab.7.Duringinference,wetakeastatic
centercropwiththesamesize.
A.4 Hyperparameters
HyerparametersusedforDiffusionPolicyonbothsimulation
and realworld benchmarks are shown in Tab. 7 and Tab.
8. Since the Block Push task uses a Markovian scripted
oracle policy to generate demonstration data, we found its
optimalhyperparameterforobservationandactionhorizon
to be very different from other tasks with human teleop
demostrations.
We found that the optimal hyperparameters for CNN-
based Diffusion Policy are consistent across tasks. In
contrast, transformer-based Diffusion Policy’s optimal
attention dropout rate and weight decay varies greatly
across different tasks. During tuning, we found increasing
the number of parameters in CNN-based Diffusion Policy
always improves performance, therefore the optimal model
size is limited by the available compute and memory
capacity. On the other hand, increasing model size for
transformer-based Diffusion Policy (in particular number
of layers) hurts performance sometimes. For CNN-based
Diffusion Policy, We found using FiLM conditioning to
pass-in observations is better than impainting on all tasks
 I K R E L '  J V I 4  I Z M X E P I 6
 7 X E X I  ' 2 2  : M W M S R  ' 2 2  : M W M S R  8 V E R W J S V Q I V
                               
 3 F W  , S V M ^ S R   W X I T W 
 4 Y W L 8  7 U Y E V I
Figure14. ObservationHorizonAblationStudy.State-based
DiffusionPolicyisnotsensitivetoobservationhorizon.
Vision-basedDiffusionPolicypreferslowbut>1observation
horizon,with2beingagoodcompromiseformosttasks.
   
    
    
    
    
    
    
    
                
   8 V E M R M R K  ( I Q S  ) T M W S H I W
 I K R E L '  J V I 4  I Z M X E P I 6
 4 Y W L  8  ( E X E  ) J J M G M I R G ]  7 U Y E V I  ( E X E  ) J J M G M I R G ]
                
   8 V E M R M R K  ( I Q S  ) T M W S H I W
 ( M J J Y W M S R 4 S P M G ]  0 7 8 1  + 1 1
Figure15. DataEfficiencyAblationStudy.DiffusionPolicy
outperformsLSTM-GMMMandlekaretal.(2021)atevery
trainingdatasetsize.
except Push-T. Performance reported for DiffusionPolicy-C
onPush-TinTab.1usedimpaitinginsteadofFiLM.
Onsimulationbenchmarks,weusedtheiDDPMalgorithm
Nichol and Dhariwal (2021) with the same 100 denoising
diffusioniterationsforbothtrainingandinference.Weused
DDIMSongetal.(2021)onrealworldbenchmarkstoreduce
the inference denoising iterations to 16 therefore reducing
inferencelatency.
Weusedbatchsizeof256forallstate-basedexperiments
and 64 for all image-based experiments. For learning-rate
scheduling, we used cosine schedule with linear warmup.
CNN-based Diffusion Policy is warmed up for 500 steps
whileTransformer-basedDiffusionPolicyiswarmedupfor
1000steps.
A.5 Data Efficiency
We found Diffusion Policy to outperform LSTM-GMM
Mandlekar et al. (2021) at every training dataset size, as
showninFig.15.
B Additional Ablation Results
B.1 Observation Horizon
We found state-based Diffusion Policy to be insensitive
to observation horizon, as shown in Fig. 14. However,
vision-based Diffusion Policy, in particular the variant with
CNN backbone, see performance decrease with increasing
observation horizon. In practice, we found an observation
horizonof2isgoodformostofthetasksforbothstateand
imageobservations.

--- Page 17 ---
DiffusionPolicy 17
H-Param Ctrl To Ta Tp ImgRes CropRes #D-Params #V-Params Lr WDecay D-ItersTrain D-ItersEval
Lift Pos 2 8 16 2x84x84 2x76x76 256 22 1e-4 1e-6 100 100
Can Pos 2 8 16 2x84x84 2x76x76 256 22 1e-4 1e-6 100 100
Square Pos 2 8 16 2x84x84 2x76x76 256 22 1e-4 1e-6 100 100
Transport Pos 2 8 16 4x84x85 4x76x76 264 45 1e-4 1e-6 100 100
ToolHang Pos 2 8 16 2x240x240 2x216x216 256 22 1e-4 1e-6 100 100
Push-T Pos 2 8 16 1x96x96 1x84x84 256 22 1e-4 1e-6 100 100
BlockPush Pos 3 1 12 N/A N/A 256 0 1e-4 1e-6 100 100
Kitchen Pos 2 8 16 N/A N/A 256 0 1e-4 1e-6 100 100
RealPush-T Pos 2 6 16 2x320x240 2x288x216 67 22 1e-4 1e-6 100 16
RealPour Pos 2 8 16 2x320x240 2x288x216 67 22 1e-4 1e-6 100 16
RealSpread Pos 2 8 16 2x320x240 2x288x216 67 22 1e-4 1e-6 100 16
RealMugFlip Pos 2 8 16 2x320x240 2x288x216 67 22 1e-4 1e-6 100 16
Table7. HyperparametersforCNN-basedDiffusionPolicyCtrl:positionorvelocitycontrolTo:observationhorizonTa:action
horizonTp:actionpredictionhorizonImgRes:environmentobservationresolution(CameraviewsxWxH)CropRes:randomcrop
resolution#D-Params:diffusionnetworknumberofparametersinmillions#V-Params:visionencodernumberofparametersin
millionsLr:leariningrateWDecay:weightdecayD-ItersTrain:numberoftrainingdiffusioniterationsD-ItersEval:numberof
inferencediffusioniterations(enabledbyDDIMSongetal.(2021))
H-Param Ctrl To Ta Tp #D-params #V-params #Layers EmbDim AttnDrp Lr WDecay D-ItersTrain D-ItersEval
Lift Pos 2 8 10 9 22 8 256 0.3 1e-4 1e-3 100 100
Can Pos 2 8 10 9 22 8 256 0.3 1e-4 1e-3 100 100
Square Pos 2 8 10 9 22 8 256 0.3 1e-4 1e-3 100 100
Transport Pos 2 8 10 9 45 8 256 0.3 1e-4 1e-3 100 100
ToolHang Pos 2 8 10 9 22 8 256 0.3 1e-4 1e-3 100 100
Push-T Pos 2 8 16 9 22 8 256 0.01 1e-4 1e-1 100 100
BlockPush Vel 3 1 5 9 0 8 256 0.3 1e-4 1e-3 100 100
Kitchen Pos 4 8 16 80 0 8 768 0.1 1e-4 1e-3 100 100
RealPush-T Pos 2 6 16 80 22 8 768 0.3 1e-4 1e-3 100 16
Table8. HyperparametersforTransformer-basedDiffusionPolicyCtrl:positionorvelocitycontrolTo:observationhorizonTa:
actionhorizonTp:actionpredictionhorizon#D-Params:diffusionnetworknumberofparametersinmillions#V-Params:vision
encodernumberofparametersinmillionsEmbDim:transformertokenembeddingdimensionAttnDrp:transformerattention
dropoutprobabilityLr:leariningrateWDecay:weightdecay(fortransformeronly)D-ItersTrain:numberoftrainingdiffusion
iterationsD-ItersEval:numberofinferencediffusioniterations(enabledbyDDIMSongetal.(2021))
B.2 Performance Improvement Calculation text Fig. 7. Each method is evaluated for 20 episodes, all
starting from the same set of initial conditions. To ensure
For each task i (column) reported in Tab. 1, Tab. 2
the consistency of initial conditions, we carefully adjusted
and Tab. 4 (mh results ignored), we find the maximum
theposeoftheTblockandtherobotaccordingtooverlayed
performance for baseline methods max baseline and
i
imagesfromthetop-downcamera.Eachevaluationepisode
the maximum performance for Diffusion Policy variant
is terminated by either keeping the end-effector within the
(CNN vs Transformer) max ours. For each task, the
i
end-zone for more than 0.5 second, or by reaching the 60
performance improvement is calculated as improvement =
i
maxoursi−maxbaselinei (positive for all tasks). Finally, the sec time limit. The IoU metric is directly computed in the
maxbaselinei top-downcamerapixelspace.
average improvement is calculated as avg improvement =
N
1 ∑i
N
improvement
i
=0.46858≈46.9%.
C.2 Sauce Pouring and Spreading
C.2.1 Demonstrations 50 demonstrations are collected,
C Realworld Task Details
and 90% are used for training for each task. For pouring,
C.1 Push-T initiallocationsofthepizzadoughandsaucebowlarevaried.
After each demonstration, sauce is poured back into the
C.1.1 Demonstrations 136 demonstrations are collected
bowl,andthedoughiswipedclean.Forspreading,location
and used for training. The initial condition is varied by
of the pizza dough as well as the poured sauce shape are
randomlypushingortossingtheTblockontothetable.Prior
varied. For resetting, we manually gather sauce towards
to this data collection session, the operator has performed
the center of the dough, and wipe the remaining dough
thistaskformanyhoursandshouldbeconsideredproficient
clean.Therotationalcomponentsfortele-opcommandsare
atthistask.
discarded during spreading and sauce transferring to avoid
accidentallyscoopingorspillingsauce.
C.1.2 Evaluation We used a fixed training time of 12
hours for each method, and selected the last checkpoint C.2.2 Evaluation BothDiffusionPolicyandLSTM-GMM
for each, with the exception of IBC, where the checkpoint aretrainedfor1000epochs.Thelastcheckpointisusedfor
withminimumtrainingsetactionpredictionMSEerrordue evaluation.
to IBC’s training stability issue. The difficulty of training Each method is evaluated from the same set of random
and checkpoint selection for IBC is demonstrated in main initial conditions, where positions of the pizza dough and

--- Page 18 ---
18
saucebowlarevaried.WeuseasimilarprotocolasinPush-
Ttosetupinitialconditions.Wedonottrytomatchinitial
shapeofpouredsauceforspreading.Instead,wemakesure
theamountofsauceisfixedduringallexperiments.
The evaluation episodes are terminated by moving the
spoon upward (away form the dough) for 0.5 seconds, or
whentheoperatordeemsthepolicy’sbehaviorisunsafe.
The coverage metric is computed by first projecting the
RGB image from both the left and right cameras onto
the table space through homography, then computing the
coverage in each projected image. The maximum coverage
betweentheleftandrightcamerasisreported.
D Realworld Setup Details
Figure16. InitialstatesforMatUnrolling
D.0.1 UR5robotstation ExperimentsforthePush-Ttask
areperformedontheUR5robotstation.
The UR5 robot accepts end-effector space positional
command at 125Hz, which is linearly interpolated from the
10Hz command from either human demonstration or the
policy. The interpolation controller limits the end-effector
velocity to be below 0.43 m/s and its position to be
within the region 1cm above the table for safety reason.
Position-controlledpoliciesdirectlypredictsthedesiredend-
effectorpose,whilevelocity-controlledpoliciespredictsthe
difference the current positional setpoint and the previous
setpoint.
TheUR5robotstationhas5realsenseD415depthcamera
recording720pRGBvideosat30fps.Only2ofthecameras
Figure17. FinalstatesforMatUnrolling
areusedforpolicyobservation,whicharedown-sampledto
320x240at10fps.
Duringdemonstration,theoperatorteleoperatestherobot posed as costs. This, coupled with a good model of the
viaa3dconnexionSpaceMouseat10Hz. Franka Panda arm, including reflected rotor inertias, allows
ustoperformgoodtrackingwithpurespatialfeedback,and
D.1 Franka Robot Station even better tracking with feedforward spatial acceleration.
ExperimentsforSaucePouringandSpreading,Bimanual Collisionavoidancehasnotyetbeenenabledforthiscontrol
Egg Beater, Bimanual Mat Unrolling, and Bimanual mode.
Shirt Folding tasks are performed on the Franka robot Note that for inference, we use the non-haptic control.
station. Futureworkintendstosimplifythiscontrolstrategyandonly
useasinglecontrollerforourgivenobjectives.
For the non-haptic control, a custom mid-level controller
The operator uses a SpaceMouse or VR controller input
is implemented to generate desired joint positions from
device(s) to control the robot’s end effector(s), and the
desired end effector poses from the learned policies. At
grippers are controlled by a trigger button on the respective
each time step, we solve a differential kinematics problem
device. Tele-op and learned policies run at 10Hz, and the
(formulatedasaQuadraticProgram)tocomputethedesired
mid-levelcontrollerrunsaround1kHz.Desiredendeffector
joint velocity to track the desired end effector velocity. The
posecommandsareinterpolatedbythemid-levelcontroller.
resultingjointvelocityisEulerintegratedintojointposition,
Thisstationhas2realsenseD415RGBDcamerastreaming
which is tracked by a joint-level controller on the robot.
VGA RGB images at 30fps, which are downsampled to
This formulation allows us to impose constraints such as
320x240at10fpsasinputtothelearnedpolicies.
collision avoidance for the two arms and the table, safety
region for end effector and joint limits. It also enables
D.2 Initial and Final States of Bimanual Tasks
regulating redundant DoF in the null space of the end
effectorcommands.Thismid-levelcontrollerisparticularly Thefollowingfiguresshowtheinitialandfinalstateoffour
valuableforsafeguardingthelearnedpolicyduringhardware bimanualtasks.Greenandredboxesindicatesuccessfuland
deployment. failedrolloutsrespectively.Sincematandshirtareveryflat
Forhapticteleoperationcontrol,anothercustommid-level objects,weusedahomographicprojectiontobettervisualize
controller is implemented, but formulated as a pure torque- theinitialandfinalstates.
controller. The controller is formulated using Operational
Space Control Khatib (1987) as a Quadratic Program
operating at 200 Hz, where position, velocity, and torque
limits are added as constraints, and the primary spatial
objective and secondary null-space posture objectives are

--- Page 19 ---
DiffusionPolicy 19
Figure18. InitialstatesforEggBeater
Figure19. FinalstatesforEggBeater
Figure20. InitialstatesforShirtFolding
Figure21. FinalstatesforShirtFolding