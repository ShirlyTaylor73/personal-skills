--- Page 1 ---
π∗
: a VLA That Learns From Experience
0.6
Physical Intelligence
AliAmin,RaichelleAniceto,AshwinBalakrishna,KevinBlack,KenConley,GraceConnors,JamesDarpinian,KaranDhabalia,JaredDiCarlo,
DannyDriess,MichaelEqui,AdnanEsmail,YunhaoFang,ChelseaFinn,CatherineGlossop,ThomasGodden,IvanGoryachev,LachyGroom,
HunterHancock,KarolHausman,GashonHussein,BrianIchter,SzymonJakubczak,RowanJen,TimJones,BenKatz,LiyimingKe,
ChandraKuchi,MarindaLamb,DevinLeBlanc,SergeyLevine,AdrianLi-Bell,YaoLu,VishnuMano,MohithMothukuri,SurajNair,KarlPertsch,
AllenZ.Ren,CharviSharma,LucyXiaoyangShi,LauraSmith,JostTobiasSpringenberg,KyleStachowicz,WillStoeckle,AlexSwerdlow,
JamesTanner,MarcelTorne,QuanVuong,AnnaWalling,HaohuanWang,BlakeWilliams,SukwonYoo,LiliYu,UryZhilinsky,ZhiyuanZhou
https://pi.website/blog/pistar06
Fig. 1: RECAP enables training VLAs with reward feedback and interventions. Our system starts with a pre-trained VLA that incorporates advantage
conditioning,allowingthemodeltolearneffectivelyfromreal-worldexperience.Foreachtask,wedeploythemodelandcollectbothautonomousrolloutsand
onlinehumancorrections.Wethenfine-tunethevaluefunctiononthisonlinedata,improvingitsestimatesofhowactionsinfluenceperformance.Fine-tuning
andconditioningtheVLAontheseupdatedadvantageestimatesinturnimprovespolicybehavior.
Abstract—Westudyhowvision-language-action(VLA)models we can flexibly specify tasks for generalist robots through
can improve through real-world deployments via reinforcement prompts. But just like people, these models will need to
learning (RL). We present a general-purpose method, RL with
practice a skill to achieve mastery. This means leveraging not
Experience and Corrections via Advantage-conditioned Policies
only on demonstration data, but also autonomously collected
(RECAP), that provides for RL training of VLAs via advantage
conditioning. Our method incorporates heterogeneous data into experiential data that allows the policy to correct the mistakes
the self-improvement process, including demonstrations, data that it actually makes in deployment, improve speed and
from on-policy collection, and expert teleoperated interventions robustnessbeyondthelevelofhumanteleoperation,andadapt
provided during autonomous execution. RECAP starts by pre-
to new deployment conditions. The foundations of learning
training a generalist VLA with offline RL, which we call π∗ ,
0.6 through autonomous practice, as formalized with reinforce-
that can then be specialized to attain high performance on
downstream tasks through on-robot data collection. We show ment learning (RL) [1], have been known for decades, but
that the π
0
∗
.6
model trained with the full RECAP method can instantiating these principles in a general and scalable robotic
fold laundry in real homes, reliably assemble boxes, and make learning system presents significant challenges: designing
espresso drinks using a professional espresso machine. On some
scalable and stable RL methods for large models, handling
ofthehardesttasks, RECAP morethandoublestaskthroughput
heterogeneous data from different policies, and setting up RL
and roughly halves the task failure rate.
trainingwithrewardfeedbackintherealworld,wherereward
I. INTRODUCTION
signals might be ambiguous or stochastic.
It’samazingwhatyoucanlearnifyou’renotafraidtotry. In this paper, we present RECAP, a method that enables
VLA models to incorporate reward feedback in all stages
Robert A. Heinlein, Have Space Suit–Will Travel
of the training pipeline, from pre-training all the way to
Practicemakesperfect:whilepeopleareremarkablyflexible training on data from autonomous execution. RECAP aims
in acquiring new skills, mastery invariably requires learning to address this problem with a general-purpose recipe that
from repeated attempts. With general-purpose robotic founda- combines demonstrations, autonomous experience, and expert
tion models, such as vision-language-action (VLA) models, interventions. Starting from the training recipe for a general-
5202
voN
91
]GL.sc[
2v95741.1152:viXra

--- Page 2 ---
Fig.2:SomeofthetaskslearnedbyRECAP.π
0
∗
.6
trainedwithRECAPcanmakeespressodrinks,assemblecardboardboxes,andfolddiverseandrealistic
laundrywithahighsuccessrate.Eachtaskinvolvesrealisticvariability–flattenedunfoldedboxessticktogetherandbend,makingespressodrinksrequires
pouringliquids,andfoldinglaundryrequiresgeneralizationtoawiderangeofclothingitems.
purposeVLAandtrainingondiversedatafrommanydifferent show, for the first time, that a general-purpose reinforcement
roboticplatforms, RECAP firstpre-trainstheVLAwithoffline learningrecipewithhumanrewardfeedbackandinterventions
RL, followed by additional training on data collected through can significantly improve both the robustness and throughput
deployments. During these deployments, the robot receives ofVLAmodelswithexperiencecollectedthroughdeployment.
(sparse) reward feedback based on the outcome of each trial,
and potentially additional expert interventions that correct
II. RELATEDWORK
mistakes. The training process follows an offline RL [2, 3] Policies trained with imitation learning are known to suffer
recipe:wetrainavaluefunctionthatevaluatesprogresstoward from compounding errors [7] and, at best, can only be as
successful task completion, and then use this value function performant as the demonstration data. The goal of this work
to estimate the advantage of each action in the dataset. By is to improve the reliability and speed of vision-language-
conditioningthepolicyonanimprovementindicatorbasedon actionpoliciesbygoingbeyondimitationlearningfromoffline
thisadvantage[4],wecanobtainanimprovedpolicy.Figure1 demonstrations. Prior works have used online interventions to
provides a high-level overview of RECAP. improveroboticmanipulationpolicies[8–11].Weadoptaform
We can use RECAP to train policies for complex tasks, of such interventions, called human-gated DAgger [10, 12].
such as folding diverse laundry, assembling boxes, or making In contrast to these works, our method uses both expert
espresso drinks. We illustrate some of these tasks in Figure 2. interventions and fully autonomous experience, resulting in
The method starts by pre-training the π∗ model with offline an RL-based framework that integrates multiple data sources.
0.6
RL on a diverse multi-task and multi-robot dataset. π∗ is There is a large body of work on using RL for autonomous
0.6
an adaptation of the π model for RL, and π is an improvement of robotic manipulation policies [13–21], in-
0.6 0.6
improvement on π [5], adding a larger backbone and more cluding methods using diffusion-based policies [22–24], in
0.5
diverse conditioning [6]. π∗ adds the ability to condition multi-task settings [25, 26], and using pre-trained multi-task
0.6
on binarized advantage values, which makes it possible to policies [27–29]. Unlike these works, we study how to scale
incorporate a value function to improve the policy. After pre- real-world RL to large VLA policies for long-horizon, fine-
training π∗ finetunes the π∗ model to a downstream task grained manipulation tasks.
0.6 0.6
withdemonstrations,andthenperformsoneormoreiterations Many recent works have studied how to improve a base
of on-robot data collection to improve the model with RL. VLA model through RL. Several works directly apply the
Training π∗ with RECAP on autonomous experience more proximal policy optimization (PPO) algorithm and variations
0.6
than doubles the throughput on some of the hardest tasks, thereof to VLA fine-tuning [30–34], yielding approaches that
and can decrease failure rates by 2× or more. This enables are difficult to extend to real-world RL in an efficient and
π∗ to reach practically useful levels of robustness: we were scalable fashion. Another line of research has explored RL
0.6
able to run it to make espresso drinks for 13 hours straight, fine-tuning on top of pre-trained VLA models, where RL
fold novel laundry items in a new home for over two hours either trains a residual policy [35, 36], fine-tunes an action
without interruptions, and assemble boxes that are used for head network [37], selects or refines actions proposed by the
real packaging in a factory. VLA [38–40], or optimizes a policy acting in the noise space
While RECAP is based on individual algorithmic compo- ofadiffusion-basedVLA[41].Someoftheseworkshavealso
nents that have been explored in prior works, the particular explored ways to distill the learned behavior back into the
combination of these components is novel, and the results VLA for end-to-end iterative improvement [35, 36, 38, 42].

--- Page 3 ---
These prior works generally use discrete actions or simple ρ (τ)=p(o ) (cid:81)T−1π(a |o )p(o |o ,a ).1 The reward
π 0 t=0 t t t+1 t t
Gaussiancontinuousactiondistributions.Acriticaldistinction function is given by r(o ,a ), and we abbreviate it to r
t t t
is that we train an entire VLA end-to-end using (iterated) to shorten notation, where r is the terminal reward. We
T
offline RL, with an expressive flow matching VLA model. can define the discounted cumulative reward, or return, as
This is made possible by a simple and scalable advantage- R(τ)=
(cid:80)T
r (wedonotuseadiscountfactor,thoughone
t=0 t
conditionedpolicyextractionmethod,whichremovesmuchof could easily be added). The goal of RL is to maximize the
the complexity of using policy gradient style objectives with cumulativereward(orreturn),learningapolicythatmaximizes
large VLA models. In our comparisons, we show that this J(π)=E [R(τ)]=E [ (cid:80)T r ]. The value function
significantly outperforms a more traditional policy gradient for a polic
τ
y
∼
π
ρπ
is then defin
τ
e
∼
d
ρπ
as V
t
π
=
(
0
o
t
)=E [ (cid:80)T r ].
t τt+1:T t=t t
based extraction scheme. We can then calculate an advantage value for an action a as
t
More closely related to RECAP in terms of methodology, Aπ(o t ,a t ) = E ρπ(τ) [ (cid:80)t t + ′= N t −1r t′ + Vπ(o t+N )] − Vπ(o t ),
a number of prior works have integrated value functions corresponding to an n-step estimate.
and end-to-end RL training of VLAs on real robots [43– Regularized reinforcement learning. Instead of maximizing
46]. For example, Huang et al. [43] apply calibrated Q- J(π), it is common to use regularization in RL, optimizing
learningtoanofflinedemonstrationdatasetforgraspingtasks, for a policy that maximizes reward while remaining close
without an online improvement phase. Zhang et al. [44] use to some reference policy π [66–70]. This is important,
ref
direct preference optimization (DPO) to optimize pick-and- for example, when we want to train for many gradient
place skills from human preferences, using online rollouts steps on the same data, in which case π typically cor-
ref
from a VLA. Finally, Zhai et al. [45], Ghasemipour et al. responds to the behavior policy that collected the training
[46] use PPO and REINFORCE respectively with time-to- data. This can be formalized via the objective J(π,π ) =
ref
completionvaluefunctionstotrainVLAsfortaskslikemoving E [ (cid:80)T γtr ] − βE [D(π(·|o)∥π (·|o))], where
τ∼ρπθ t=0 t o∼ρπθ ref
a bowl, unfolding a mat, and pushing objects on a table. D denotes some divergence metric. For the case where
In contrast to these prior works, we describe an iterated D is the KL divergence, we have the well-known result
offline RL framework for VLAs with multiple advantages. that πˆ(a|o)∝π
ref
(a|o)exp(Aπref(o,a)/β) is the solution to
First, our method supports high-capacity diffusion and flow- max J(π,π ), with Lagrange multiplier β [67–70]. Our
π ref
based VLAs, unlike the discrete-action models studied in advantage-conditioned policy extraction method is based on
prior works. Second, we avoid the need for on-policy PPO a closely related but less well-known result: if we de-
or REINFORCE by using an advantage conditioning strategy fine the policy πˆ(a|o)∝π
ref
(a|o)p(I|Aπref(o,a))β, where
for policy extraction, which can utilize all prior (off-policy p(I|Aπref(o,a)) = g(Aπref(o,a))/ (cid:82) g(Aπref(o,a′))da′ is the
or offline) data. Lastly, our evaluation consists of complex, probability of any action a improving over π as measured
ref
dexterous, and temporally extended tasks, where our method byamonotonicallyincreasingfunctiong,thenπˆ isguaranteed
increases throughput by about 2× while handling deformable toimproveoverπ ,i.e.,J(πˆ)≥J(π )[4,71].Wewilluse
ref ref
objects, liquids, and multi-stage tasks. this property in deriving our policy extraction method in Sec-
Prior works have explored the idea of conditioning the tionIV-B.Usingthisdefinitionwecanthenobtainaparamet-
policy on rewards, values, and advantages [47–56], including ric policy from the closed form definition of πˆ by solving the
methods that use classifier-free guidance [4]. We extend this following minimization problem: min θ E s∼ρπref [KL(πˆ,π θ )].
approach to pre-train and fine-tune a large-scale generalist
IV. RLWITHEXPERIENCEANDCORRECTIONSVIA
VLA policy [5], incorporating a variety of data sources (in-
ADVANTAGE-CONDITIONEDPOLICIES(RECAP)
cluding demonstrations, interventions, and autonomous policy
roll-outs) to learn real robotic manipulation tasks. Recent Our method consists of the follow steps, which can be
research has also studied how to effectively train multi- repeated one or more times to improve a base VLA model:
task,language-conditionedrewardfunctions[57–63]andvalue 1) Data collection. We run the VLA on the task, labeling
functions [45, 64, 65]. Building on these works, we also train eachepisodewithtaskoutcomelabels(whichdetermine
alanguage-conditioneddistributionalvaluefunction,whichal- the reward), and optionally providing human interven-
lows us to estimate state-action advantages for our advantage- tions to provide examples of corrections for mistakes in
conditioned VLA training framework. the earlier iterations.
2) Valuefunctiontraining.Weuseallofthedatacollected
so far to train a large, multi-task value function, which
III. PRELIMINARIES
we refer to as Vπref, that can detect failures and judge
the expected time to task completion.
Reinforcement learning. We consider the standard RL
3) Advantage conditioned training. To improve the VLA
setting in which an agent, given by a policy π(a |o ),
t t policywiththisvaluefunction,weincludeanoptimality
selects actions a given an observation o ∈ O. We
t t indicator based on advantage values derived from this
define a trajectory as τ =(o ,a ,··· ,o )∈O×A···O.
0 0 T
A distribution over trajectories ρ (τ) is induced by the
π 1Forsimplicity,weassumetheobservationotconstitutesavalidMarkovian
policy π(a t |o t ) and the stochastic dynamics p(o t+1 |o t ,a t ): state.Whilenottrueingeneral,itisacommonsimplificationinroboticRL.

--- Page 4 ---
value function in the VLA prefix. This “advantage
conditioned”recipeprovidesasimpleandeffectiveway
toextractamoreoptimalpolicyfromourvaluefunction
with suboptimal data.
Figure 1 illustrates the overall structure of the training pro-
cess, while Figure 3 provides more detailed specifics of the
valuefunctionandpolicyarchitectures.Ourpre-trainingphase
consists of performing steps (2) and (3) above on our entire
pre-training dataset, which consists of tens of thousands of
hoursofdemonstrationsfromnumeroustasksandavarietyof
different robots. Then, we perform steps (1), (2), and (3) one
ormoretimestofurtherimprovetheVLAwithautonomously
collected data. We describe the value function training and
policy training steps below, and then present our specific
instantiation of this approach for training π∗ in Section V.
0.6
A. Distributional value function training
Fig. 3: Interaction between the π∗ VLA and value function during
To train a value function that can act as a reliable critic 0.6
for any task in our pre-training or post-training stages, we f R o E ll C ow A s P t t h r e a K in I in re g c . i T p h e e [7 π 3 0 ∗ ] . , 6 w V it L h A ne u x s t e -t s ok a e p n re p - r t e ra d i i n c e ti d on V o L n M m b a a n c y k d b a o t n a e s . o T u r r a c i e n s in i g n
represent Vπref with a multi-task distributional value function pre-training,andanflow-matchingaction-expertwithstopgradient.TheVLA
is conditioned on a binarized advantage indicator, obtained from a separate
p (V|o ,ℓ)∈∆ [72], mapping the observations o and
ϕ t B t valuefunctioninitializedfromapre-trainedbutsmallerVLMmodel.
language command ℓ to a distribution over B discretized
valuebins.Inourimplementation,thisvaluefunctionusesthe
samearchitectureastheVLApolicy,butwithasmallerVLM
backbone. Using R (τ) =
(cid:80)T
r to denote the empirical
it needs to effectively utilize diverse off-policy data, compris-
t t′=t t′ ing the initial demonstrations, the expert interventions, and
return of a trajectory τ from time step t until the end, we
autonomous episodes from both the latest policy and older
trainp (V|o ,ℓ)byfirstdiscretizingtheempiricalreturnvalue
ϕ t policies. This is closely related to the challenge faced by
R (τ) into B =201 bins (using RB to denote the discretized
t t offline RL methods [2, 3]. Second, it needs to be scalable
returns), and then minimizing the cross-entropy H over the
and easily to apply to large VLA models, including models
trajectories in the current dataset D:
that use flow matching or diffusion to generate actions. Third,
(cid:34) (cid:35)
itneedstoeffectivelyutilizebothgood(near-optimal)andbad
(cid:88)
minE τ∈D H(R t B(τ),p ϕ (V|o t ,ℓ)) . (1) (suboptimal) data, which is important if we want to improve
ϕ
ot∈τ the policy using autonomous experience.
This is a Monte Carlo estimator for the value function of Among the existing methods for policy extraction, pol-
the policy represented by the dataset D (i.e., the behavior icy gradient methods (including regularized policy gradients
policy π ). We can extract a continuous value function (and and reparameterized gradients) are perhaps the most widely
ref
thus an advantage) from the learned value distribution using used [66, 74], but these methods are difficult to apply to flow
Vπref(o
t
,ℓ)= (cid:80)
b∈[0,B]
p
ϕ
(V =b|o
t
)v(b),wherev(b)denotes matching models, which do not readily provide a tractable
thevaluecorrespondingtobinb.Duringthepre-trainingphase, log-likelihood, making them hard to scale up to modern VLA
the dataset D corresponds to the human demonstrations, and architectures(seecomparisonsinSectionVI).Analternativeis
the value function captures the expected return for the task touseweightedregressionmethods,suchasAWR[68,75,76],
andmetadataweconditionon,whileonsubsequentiterations, which implicitly provide for regularization to the behavior
it skews toward a weighted combination of the return of the policy and use a simple (importance-weighted) supervised
demonstrations and the learned policy. learning objective. However, these methods discard or signifi-
While this on-policy estimator is less optimal than a more cantlydownweightasignificantportionofthedata,effectively
classic off-policy Q-function estimator, we found it to be implementing a kind of filtered imitation technique. Instead,
simple and highly reliable, while still allowing for substantial we use a variant of advantage conditioning [48], where the
improvement over imitation learning. Our method could be policy is trained on all of the data with supervised learning,
extendedtoaccommodateoff-policyestimatorsinfuturework. but with an additional input indicating how optimal the action
isbasedontheadvantage.Thisiscloselyrelatedtoavarietyof
B. Policy extraction via advantage conditioning methods in the literature that propose to condition the policy
Once we have the value function Vπref, we need a way on some function of the resulting trajectory [47, 50].
to train an improved policy using this value function. This The specific formulation in our method is most closely re-
is called policy extraction. An effective policy extraction latedtoCFGRL[4].BuildingontheformulationinSectionIII,
method in our setting needs to satisfy several criteria. First, we can apply Bayes rule to rewrite the probability of policy

--- Page 5 ---
Successful Episode: Folding Laundry Failure Episode: Open Fridge and Take Out Water Filter
Left arm swings up and crumples the folded shirt Recovers and folds Attempts to open fridge door Successfully opens fridge door Tips over water filter
Time (s) Time (s)
Fig.4:Visualization of the value functions.Wetrainamulti-taskvaluefunctiontopredictthenumberofstepstosuccess,normalizedbymaximumtask
length to (−1,0), where 0 corresponds to successful completion. We visualize the value function output on a folding task that finished successfully (left),
andanunsuccessfulexampleofamanipulationtaskfromthepre-trainingdataset(right).Theredpartshighlightadropinvalue,andgreenpartshighlight
increases;imagesontopshowthecorrespondingframesoftheepisode.ThevisualizationshowsthattheVFcorrectlyidentifiesmistakesintheepisode,as
wellasthespeedofprogress.
improvement as p(I|Aπref(o,a))=π
ref
(a|I,o)/π
ref
(a|o). Ap- deployed policies. To include human corrections, we found it
plyingthistooursettingandincludinglanguageconditioning, useful to force I = True (i.e., positive) for actions provided
t
we can obtain an alternative closed form for the improved ashumancorrectionsduringautonomousrollouts.Thischoice
regularized policy described in Section III as isreasonableifweassumethathumanexpertsalwaysprovide
good corrective actions. As we will discuss in Section V, in
(cid:18)
π (a|I,o,ℓ)
(cid:19)β
πˆ(a,|o,ℓ)∝π (a|o,ℓ) ref . (2) practice our VLA model produces both discrete and continu-
ref π (a|o,ℓ)
ref ous outputs, with the continuous distribution represented via
For the special case β =1, πˆ(a,|o,ℓ)=π (a|I,o,ℓ). flowmatching.Therefore,therealtrainingobjectivecombines
ref
We can therefore represent πˆ without needing to explicitly likelihoods for the discrete values with the flow matching
represent the improvement probability p(I|Aπref(o,a)), if we objective for the continuous values.
train the policy so that it can represent both π (a|o,ℓ) and In practice, we pre-train one model to represent
ref
π ref (a|I,o,ℓ). This principle is similar to the approach in π θ (a t |I t ,o t ,ℓ) on our entire pre-training dataset, and then
classifier-free guidance, where a diffusion model is trained perform one or more iterations of our method with on-policy
to model the data both with and without a conditioning rollouts (and, optionally, expert corrective interventions) for
variable [4]. We assume the improvement indicator I follows each task.
a delta distribution
C. Method summary
p(I|Aπref(o,a,ℓ))=δ(Aπref(o,a,ℓ)>ϵ
ℓ
), WeprovideanoverviewofourfullmethodinAlgorithm1.
As summarized at the beginning of this section, the method
with a task dependent improvement threshold ϵ . This thresh-
ℓ can be fully defined through application of three subroutines:
old allows us to control the optimality indicator, and mini-
collecting data through autonomous rollouts (with optional
mizes the need for finding an attenuation factor β to sharpen
correctiveinterventionsfromanexpert),trainingavaluefunc-
the improvement conditioned distribution after training.2 The
tion according to Equation 1, and training a policy according
policyobjectivethencorrespondstominimizingthefollowing
to Equation 3. The only thing that changes between different
negative log-likelihood:
steps of the method is the data provided to each subroutine:
(cid:104) (cid:105)
minE −logπ (a |o ,ℓ)−αlogπ (a |I ,o ,ℓ) , the pre-training stage uses all prior demonstration data, and
θ
Dπref θ t t θ t t t
(3) the training process for the specialists for each skill ℓ(i)
where I t =1(cid:0) Aπref(o t ,a t ,ℓ)>ϵ ℓ (cid:1) . uses additional autonomous data. In practice, the specialists
are fine-tuned from the pre-trained model, while the final
The advantage values Aπref(o
t
,a
t
,ℓ) are obtained from the
generalist is trained from scratch. Additional details on the
value function in the previous section, and α is a trade-
method are provided in Appendix F.
off hyperparameter. In practice, the dataset D consists of
πref
all of the data collected so far, including all demonstrations V. IMPLEMENTATION,MODEL,ANDSYSTEMDETAILS
and autonomous task attempts, and the reference policy π
ref We instantiate RECAP with a VLA that we call π∗ . π∗
is therefore a mixture of human behavior and previously 0.6 0.6
is based on the π VLA, which is an evolution of the π
0.6 0.5
VLA [5] with a few improvements that we detail in the ac-
2Priorwork[4]insteaduniformlychoseϵ=0andtunedβattesttime,as
inclassifier-freeguidance(CFG).However,highCFGweightscandrivethe companying model card [6]. π∗ additionally adds the ability
0.6
actiondistributiontothecornersofitssupport(leadingtoaggressivebehavior) condition on the binarized advantage indicator I , making it
t
andwouldnotaffecttheautoregressivepartofthemodel.Wefounditeasierto
obtaingoodresultsbyinsteadusingthethresholdϵ ℓtotradeoffregularization
suitable for RL training with RECAP. The model architecture
andoptimality. is illustrated in Figure 3. We train a value function alongside

--- Page 6 ---
Algorithm 1 RL with Experience and Corrections via sub-task prediction runs at a lower frequency than action gen-
Advantage-conditioned Policies (RECAP) eration. During training, the model also predicts a tokenized
Require: multi-task demonstration dataset D demo representation of the action chunk a t:t+H , using the FAST
1: Train V pre on D demo using Eq. 1 tokenizer [77], as part of the KI recipe [73]. We denote these
2: Train π pre on D demo using Eq. 3 and V pre discretized actions aℓ t:t+H . The action expert does not receive
3: Initialize D ℓ with demonstrations for ℓ these as input, such that discrete and continuous actions are
4 5 : : T T r r a a i i n n V π ℓ ℓ 0 0 f f r r o o m m π V p p r r e e o o n n D D ℓ ℓ u u s s i i n n g g E E q q . . 3 1 and V ℓ 0 p li r k e e d li i h ct o e o d d in lo d g ep π e θ n ( d a e t n :t t + ly H . , T a h ℓ t i :t s + r H es , u ℓˆ l | t o s t i , n ℓ) t . he Si fi n n c a e l w tr e ain p i r n e g di l c o t g ℓˆ -
6: for k =1 to K do first, we can factorize this log-likelihood according to:
7: Collect data with π ℓ k−1, add it to D ℓ logπ (cid:0) a ,aℓ ,ℓˆ|o ,ℓ (cid:1) =logπ (cid:0) ℓˆ|o ,ℓ (cid:1)
9 8 : : T T r r a a i i n n π V ℓ ℓ k k f f r r o o m m π V p p r r e e o o n n D D ℓ ℓ u u s s i i n n g g E E q q . . 3 1 and V ℓ k θ + t: l t o + g H π θ (cid:0) t a :t ℓ t + :t H +H |o t t ,ℓ,ℓˆ(cid:1) +log θ π θ (cid:0) a t t :t+H |o t ,ℓ,ℓˆ(cid:1) .
10: end for B. From π to π∗ with advantage conditioning
0.6 0.6
To incorporate information about the advantage into the
policy, we expand the model inputs to contain an additional
the VLA, following the method described in Section IV-A.
improvement indicator as an additional text input, inputting
This value function is also initialized from a VLM. Training
“Advantage: positive” when I = True, and “Advantage:
this value function and VLA with RECAP results in our final t
negative” otherwise. The VLA model is otherwise the same
model, which we call π∗ . In this section, we first elaborate
0.6 as described in Section V-A. The advantage indicator appears
on the design of our model and how it can be extended to use
in the training sequence after ℓˆbut before the (discretized and
advantage values from the value function, then describe the
continuous) actions, such that only the action log-likelihoods
reward function and value function, and then elaborate on the
are affected. The continuous part of the log-likelihood cannot
training and data collection process in our implementation.
beevaluatedexactly,andinsteadistrainedviatheflowmatch-
A. The π model ing loss [79]. It is possible to draw a close parallel between
0.6
flow matching and diffusion (under some assumptions), and
The π model [6] is derived from the π model, which
0.6 0.5
the latter in turn can be interpreted as a lower bound on the
can flexibly represent chunked action distributions via flow
log-likelihood[80],sowecanroughlymotivatethesumofthe
matching and produce intermediate text for high-level policy
log-likelihood of the discrete actions and the flow matching
reasoning. It uses the Knowledge Insulation (KI) training
lossonthecontinuousactionsasalowerboundontheoverall
procedure [73], which trains the entire model end-to-end on
action likelihood:
continuous actions and discretized tokens (including actions
discretized via FAST [77]), while using a stop gradient to logπ (a ,aℓ |I ,o ,ℓ,ℓˆ)≥
θ t:t+H t:t+H t t
prevent the flow-matching action expert from impacting the (cid:104)
E logp (aℓ |I ,o ,ℓ,ℓˆ)−
restofthemodel.Pre-trainingusesbothrobotdataandvision- η,ω θ t:t+H t t , (4)
language co-training data from the web. α (cid:13) (cid:13)ω−a −f (aη,ω ,I ,o ,ℓ,ℓˆ) (cid:13) (cid:13) 2(cid:105)
π improves on π in several ways: (i) The pre-training η(cid:13) t:t+H θ t:t+H t t (cid:13)
0.6 0.5
dataset is augmented with additional data from multiple robot with aη,ω = ηa +(1−η)ω, ω ∼ N(0,I) denoting
t:t+H t:t+H
platforms.(ii)ThebaseVLMisGemma3[78]4Bmodel.(iii) the noised action, where η ∈ [0,1] is the flow matching time
Thesizeoftheactionexpertisincreasedto860Mparameters. index and f denotes the continuous outputs of the diffusion
The model can be written as π θ (a t:t+H ,ℓˆ|o t ,ℓ), where expert. α η θ is a loss weighting term (which can optionally
o t = [X1 t ,...,Xn t ,q t ] contains camera images X, the robot’s be noise dependent). Full details for the loss are provided in
configurationq,andℓ=ℓ t +sisthelanguageinputconsisting Appendix C.
of the overall task prompt ℓ t (e.g., “make me an espresso”), During training, we randomly omit the indicator I t instead
as well as additional language inputs s providing metadata of tuning the loss multiplier α to allow us to either directly
that further modulates how the task is performed. The model sample from the policy with I =True (which corresponds to
t
produces action chunks a t:t+H , which consists of joint angles setting β = 1 in Equation (2)), or to use both a conditional
and gripper commands at 50 Hz, using a separate “action andunconditionalmodeltoimplementclassifier-freeguidance
expert” — a dedicated set of weights (860M parameters) (CFG), which enables inference with β >1. See Appendix E
that are trained with flow matching specifically for action for details.
generation, but can attend to the activations in the rest of the
model. The model also produces tokenized discrete outputs ℓˆ, C. Reward definition and value function training
which includes a textual representation of the next predicted Sinceouraimistodevelopageneralandbroadlyapplicable
sub-task (such as “pick up the coffee cup”) used for high- method for training VLAs from experience, we use a general
level decision-making. Since the actions are generated after ℓˆ, sparse reward definition that can be applied to essentially any
action generation is effectively conditioned on this predicted task. For each episode, we obtain a label indicating whether
sub-task,providinghigh-levelguidance.Atinferencetime,the that episode was successful. We derive the reward from

--- Page 7 ---
this episode-level success label such that the value function
corresponds to the (negative) number of steps until successful
completion of the episode. This is equivalent to the following
reward function, where T corresponds to the last step in the
episode, and C is a large constant that is chosen so as to
fail
ensure that failed episodes have low values:

0 if t = T and success

r = −C if t = T and failure (5)
t fail
−1
otherwise.
With this reward function, we train the value function to
predict the (negative of the) number of remaining steps until Fig. 5: The robot setup used in our experiments. π∗ is trained on data
0.6
success for successful episodes, and a large negative value for from many different robots in pre-training. For the iterative improvement
failedepisodes.Inpractice,wenormalizethevaluespredicted experiments, we use a static bimanual system with two 6 DoF arms with
paralleljawgrippers.Thearmsarecontrolledat50Hzwithjointpositions.
to be between (−1,0). Since we train on diverse tasks that
Observations consist of joint and gripper positions, as well as images from
have very different typical lengths, we normalize the values threecameras:abasecameramountedbetweenthearms,andawrist-mounted
per task based on the maximum episode length of the task. cameraoneacharm.Thesetupcanbemountedflexibly,e.g.onatable.
The value function takes as input the same language inputs
astheπ∗ VLA,andusesthesamearchitecturedesign,witha
0.6
provide corrections. These corrections can show the policy
smaller670MparameterVLMbackbonethatisalsoinitialized
how to avoid catastrophic failures or how to recover from
from Gemma 3 (see Figure 3). To prevent overfitting, we also
mistakes.Note,however,thatthecorrectionsaloneareunlikely
co-train the value function on a small mixture of multi-modal
to fix all issues: intervening during autonomous execution is
web data. Figure 4 show visualizations of the value function
a disruptive event, and even expert human operators cannot
on some examples of successful and failure episodes, with
guarantee a consistent quality of interventions nor improve
additional visualizations in Figure 13 in Appendix B.
subtle aspects of the behavior, such as overall speed. Thus,
D. Pre-training,datacollection,andlearningfromexperience the corrections serve more to fix large mistakes and overcome
challengeswithexploration,anddonotbythemselvesprovide
The data mixture used in the pre-training phase of our
for optimal supervision, in contrast to theory [7]. Recall from
modellargelyfollowstherecipeusedbyπ [5],withvision-
language data from the web, prediction 0 o . f 5 subtasks ℓˆ, and Section IV-B that we force I t = True for all corrections,
but otherwise the entire episode (both the autonomous parts
prediction of low-level actions on a variety of tasks from
and the corrections) are optionally added to the dataset D
many different robots. We note that, after pre-training, π∗ ℓ
0.6 regardless of whether or not a correction was provided.
canperformmanymoretasksthantheonesusedinevaluation
After data collection, we finetune the value function on
in Section VI. During pre-training, we first train the value
all of the data collected for the task so far, and then use it
function on the same dataset, predicting (the negative of) the
to finetune the policy with updated indicators I , using the
number of steps to successful completion of each task. Then t
sameprocedureasinpre-training.Boththevaluefunctionand
we estimate the per-task improvement threshold, ϵ , used in
ℓ
policy are finetuned from the pre-trained checkpoint, rather
determining the advantage-based improvement indicator I .
t
than the policy and value function from the last iteration.
We set ϵ to the 30% percentile of values predicted by the
ℓ
We found this to be useful for avoiding drift over multiple
value function for the task ℓ. We then run the value function
iterations,thoughitmaybepossibletoalsoobtaingoodresults
on-the-fly during VLA training to estimate Aπref(o
t
,a
t
,ℓ) for
by consistently finetuning from the last model.
each example, and then use it to compute I based on ϵ . I
t ℓ t
We can repeat this process for several iterations as needed,
is included as an input to π∗ as described in Section V-A.
0.6 thoughinpracticewefoundthatevenoneiterationoftenleads
As we use a relatively small VLM backbone (670M) for
to significantly improved results.
the value function, on-the-fly inference of the value function
incurs minimal additional cost during VLA training.
VI. EXPERIMENTALEVALUATION
After pre-training we start a policy improvement loop for
the target task. We first finetune π∗ with demonstration data In our experimental evaluation, we use RECAP to train the
0.6
D for the target task ℓ. We fix the indicator I to True in this π model on a set of realistic tasks: making espresso drinks,
ℓ t 0.6
stage, which we found to lead to slightly better results, such folding diverse laundry, and assembling boxes. Each task re-
that this stage corresponds to supervised finetuning (SFT). quiresmultiplesteps,rangingfrom5to15minutesinduration,
This results in the initial policy π0, which is then used complexmanipulationbehaviors(constrainedforcefulmanipu-
ℓ
to collect additional data that is added to D . While some lation,pouringliquids,manipulatingclothandcardboard,etc.),
ℓ
of the episodes are collected fully autonomously, some are andfastexecutiontoprovideforhighthroughput.Weillustrate
monitored by an expert teleoperator who can intervene to the robotic platform used in our experiments in Figure 5. We

--- Page 8 ---
Fig.6:Illustrationsofthetasksusedinourexperiments.Tasksincludethreedifferentlaundryvariants,assemblingboxes,andmakingcoffeedrinkswith
anespressomachine.
give details on the tasks and baselines below, followed by commercialespressomachine.Whileourcafepolicycanmake
quantitative experiments. manydrinks(lattes,icedAmericanos,espresso,etc),andeven
clean the espresso machine with a towel, for the purposes of
A. Evaluation Tasks
our quantitative experiments we focus on the double espresso
Our quantitative evaluations and comparisons use three shot task. This entails picking up the portafilter, placing it
broad task categories each with individual task variants: laun- on the grinder and grinding beans into it, tamping the ground
dry folding, coffee making, and box assembly. We summarize coffeebeans,lockingtheportafilterintotheespressomachine,
the tasks below, with illustrations in Figure 6: bringingoverthecup,extractingthefullshotofespresso,then
Laundry (t-shirts and shorts). This is the standard laundry serving. Success is measured as completing all steps within
folding task in the π paper [81]. This task entails retrieving 200 seconds without critical mistakes (such as dropping the
0
either a T-shirt or shorts from a basket with variable initial portafilter or spilling the coffee).
conditions, flattening, folding. Success requires one clothing Box assembly. We evaluate our policy on the problem of
item to be folded and stacked in the top right corner of the assembling packaging boxes in a real-world factory deploy-
table within 200 seconds. mentscenario.Boxassemblyinvolvesfoldingacardboardbox
Laundry (diverse items). The diverse laundry task requires startingfromaflattenedcardboardsheet,attachingalabelonto
folding a much larger variety of items, considering 11 item it and placing the box in the appropriate spot in a crate. For
types, including towels, button-up shirts, sweaters, jeans, T- the purposes of the quantitative experiments, we focus on all
shirts, shorts, polos, skirts, long sleeve shirts, socks, and portions of the task and count overall success as going from
underwear.Toobtainalow-variancemetricinourexperiments, a flattened to an assembled and stacked box in under 600
we measure performance on one of the most challenging seconds.
items – the button-up shirt. However, the policy is trained
on all items, and the accompanying videos show results for B. Comparisons and Ablations
a variety of clothing. Success is defined as having the target
itemcorrectlyfoldedandplacedonastackonthetablewithin
We compare RECAP to several baselines:
500 seconds. Pre-trained π 0.5 [5]. This baseline does not use RL and does
Laundry (targeted failure removal). The final version of not leverage RECAP.
the laundry folding task considers a much more structured Pre-trained π 0.6 [6]. It does not include the advantage indi-
setup for use in our ablation experiments, in which the task cator I t , and is pre-trained with supervised learning.
involves folding a single orange T-shirt from a fixed flattened RL pre-trained π∗ . It is pre-trained with RL alongside
0.6
initial condition. We place the highest emphasis on success, its value function, and includes an advantage indicator I t as
withastrictsuccesscriteriathatrequirestheshirttobefolded described in Section V-D.
correctlywiththecollaralwaysfacingupwithin200seconds. π∗ offlineRL+SFT.Thismodelistrainedbyfinetuningthe
0.6
We found this task to be useful for assessing whether RECAP base π∗ pre-trained checkpoint with demonstration data for
0.6
canremovespecificundesirablebehaviorsviaRL(inthiscase, the target task. We refer to this finetuning as “SFT” because
placing the collar facing down rather than up). the advantage values are fixed to True for all demonstrations.
Cafe (double shot espresso). We evaluate our policies on We find that this combination of the offline RL pre-trained
the challenging long-horizon task of making coffee with a π∗ model with high-quality SFT outperforms standard SFT
0.6

--- Page 9 ---
Fig. 7: Throughput. We show the number of successfully completed tasks per hour for laundry (simple and diverse), espresso making, and box assembly.
Errorbarsshowstandarderror.Thismetricmeasuresbothsuccessandspeed.Inallcases, RECAP appliedtoπ
0
∗
.6
(Ours)leadstosubstantialimprovements
inthroughput.RECAPhasthehighestimpactonthroughputfordiverselaundryandespressotasks,morethandoublingsuccessfulcompletionsperhour.
Fig.8:Successrates.Weshowtheabsolutesuccessrateswithstandarderror.EachstageofRECAPimprovesperformanceacrossthetasks,withthechallenging
diverselaundryandespressotasksseeingthelargestgainssuccessrate,correspondingtomorethan2×reductioninfailurerates.Fortheboxassemblytask
weshowthesuccessrateforthedifferentsubtasks.RECAPleadstothemostconsistent(andhighest)successacrossallsubtasks.
(withoutofflineRLpre-training),andprovidesagoodstarting to judge the episode with respect to multiple quality metrics,
point for RL with on-robot data. and we aggregate these quality indicators into a success label.
π∗ (ours). This is the final model trained with RECAP on 1) Howmuchdoes RECAP improvethepolicy?: Toanswer
0.6
the target task, including both autonomous rollouts and expert this question, we present the main quantitative results in
corrections. By default we evaluate with β = 1. In some Figures 7 and 8. Across all tasks, the final π∗ significantly
0.6
experiments we also consider inference with CFG, which improves over the base (supervised) π 0.6 model, the RL pre-
corresponds to β >1. trained π∗ model, and the offline RL + SFT π∗ model.
0.6 0.6
We also consider two alternative policy extraction methods Throughput more than doubles on the diverse laundry folding
in the literature as comparisons for our advantage-conditioned andespressotasksfromincludingon-robotdata(theimprove-
approach,bothofwhichusethesameon-robotdataasRECAP mentfromoffline RL + SFTtothefinalπ
0
∗
.6
model),andthe
but a different policy learning method: rate of failure reduces by about a factor of two. On the easier
AWR. Starting from the same pre-trained model π (with- laundry task (t-shirts and shorts), the success rate is already
0.6
out advantage conditioning) we fine-tune using advantage closetothemaximumaftertheSFTphase,butthroughputstill
weighted regression [68], based on advantages extracted from increases by a significant margin with the final model.
our value-function. On all of the tasks except diverse laundry, the success rate
PPO.WeimplementavariantofDPPO/FPO[23,82]inwhich of the final π∗ model is in the 90%+ range. This makes it
0.6
wecalculatelikelihoodsbasedonthesinglestepdiffusionob- feasible to use in practical settings, such as making espresso
jective and use an alternative definition of the PPO constraint drinks at the office or assembling boxes in a factory, as
following SPO [83] (see Appendix D for details). shown in the accompanying videos. For the box assembly
task,Figure8(right)containsabreakdownofthetasksuccess
C. Quantitative results
over its four stages: picking up a box sheet, building the box,
We use two metrics in our evaluation: throughput and labeling the box, and placing it at an available spot in a crate.
success rate. Throughput measures the number of successful π∗ attainshighersuccessratesforallofthestagescompared
0.6
task executions per hour, thus capturing both speed and to the other models. The majority of failures on these stages
success rate into one practically relevant quantity. Success happenbecausethepolicyrunsoutoftime.Theaccompanying
rate measures the proportion of episodes that succeed, and videos present time lapses where each of the tasks is run for
is derived from human-provided annotations. Raters are asked multiple hours.

--- Page 10 ---
Fig.11:Comparisonofdifferentpolicyextractionmethods.RECAPapplied
toπ∗ achievesbyfarthehighestthroughputforthelaundrytaskcompared
0.6
toAWRandPPO.
Fig. 9: Improvement in throughput over multiple iterations. Both tasks
improve significantly in throughput as we take more iterations of RECAP,
withboxassemblingfirstdroppingandthenimprovingsignificantly.
Fig.10:Improvementinsuccessrateovermultipleiterations.Thelaundry
taskquicklyreachesthemaximumsuccessrate(butcontinuestoimprovein
Fig. 12: Failure mode removal. Here we apply RECAP on a variant of
throughputasshowninFigure9,whileboxassemblycontinuestoimprove.
the laundry task with one item but a very strict success criteria. RECAP is
particularlyeffectiveatremovingfailuremodesthatwouldbeconsiderednon
successfulunderthestrictcriteria.Therefore,ourmethodcanalsobeusedto
2) HowmuchdoesRECAPimproveπ∗ overmultipleitera- alterapolicy’sbehaviorwithrelativelylittledataeffectively.
0.6
tions?: Wenextelucidatehowtrainingwith RECAP improves
policiesthroughmultipleiterationsofdatacollectionandtrain-
ing. We study the T-shirt and shorts folding task and the box improves throughput. For the box assembly task, we see clear
assemblytask.FortheT-shirtfoldingtask,onlydatacollected improvements in the success rate over both iterations. While
with autonomous evaluation (without human corrections) is there are still some failures (especially when placing the box
used to perform policy improvement over two iterations, in on the stack at the end), the final policy achieves a success
ordertoevaluatehowwellourmethodcanimprovethepolicy rate of about 90% both for folding the box and labeling it in
viaRLalone.Wecollect300trajectoriesonfourrobotsineach the allocated time limit of 600 seconds.
iteration.Boxassemblyusesbothautonomoustrialsandtrials 3) How does the advantage-conditioned policy extraction
with expert teleoperator interventions, with 600 autonomous method in RECAP compare to other methods?: We compare
trials and 360 trials with interventions in each iteration. our advantage conditioned policy extraction method from
We plot the throughput over iterations in Figure 9, com- Section IV-B to other methods in the literature: AWR and
paring two iterations of RECAP, denoted by i = 1, i = 2 PPO. We use the T-shirts and Shorts task for this comparison.
respectively. The final iteration, labeled (Ours), corresponds To ensure a controlled comparison, we use the same data for
to the overall best result for these tasks presented in the thesecomparisonsthatwasusedtotrainourfinalmodel.This
previous section. We also compare the initial data collection provides a slight advantage to the baselines, since they have
policy, which uses the offline RL pre-trained π
0
∗
.6
model with access to better data that was collected while running RECAP.
SFT finetuning. For both tasks, π∗ improves over the two The results are shown in Figure 11. While both AWR and
0.6
iterations. In the laundry task we can see steady improvement PPO can attain reasonable results, they both fall far short of
yielding an overall 50% improvement in throughput. For the our method, and struggle to improve over the offline RL +
long-horizon box assembly task, more data is needed to yield SFT π∗ model. For PPO, we had to use a small trust-region
0.6
a significant improvement, but after the second iteration we constraint (η = 0.01) to stabilize training in this off-policy
see a 2× improvement in throughput. setting, and while this makes training stable, the method does
We also show the success rate over the iterations in Fig- notachievegoodperformance.AWRcanachieveareasonable
ure 10. For the laundry task, the first iteration already raises success rate, but leads to much slower polies with lower
thesuccessratetoover90%,whiletheseconditerationmainly throughput.

--- Page 11 ---
4) Can RECAP significantly alter policy behavior with where the policy and value function are updated in real time
relatively little data and remove a failure mode?: While the asdataiscollected.Wemakethisdecisionoutofconvenience,
preceding experiments have focused on holistic end-to-end but extending our approach into a fully concurrent online RL
evaluations of policy performance, we can also zoom in on framework is a promising direction for future work.
a specific failure mode to examine whether RL training with More broadly, training VLAs with RL is perhaps the most
RECAP can remove a specific mistake from the policy. To direct path to get to performance levels that are adequate for
answerthisquestion,weuseaversionofthelaundrytaskwith real-world use cases. RL with VLAs presents a number of
a strict success criterion, which requires the policy to fold a challenges, from the difficulty of large-scale RL training of
t-shirt with the collar centered and facing up. Each episode is high capacity models to sample complexity, autonomy, and
initialized with a specific adversarial condition in which the delayedfeedback.WhileexistingRLframeworksdesignedfor
shirt is placed flat on the table in such a way that the baseline smaller-scale systems or “virtual” domains such as LLMs can
offline RL + SFT policy often fails to fold it correctly. As provide a good starting point, more research will be needed
shown in Figure 12, applying RECAP in this setting for two to make RL a practical tool for VLA training. We hope that
iterations (collecting 600 trajectories in each iteration) results our work represents a meaningful step in this direction.
inapolicythatsucceeds97%ofthetime,andwithhighspeed.
Thus we conclude that RECAP can be effective at removing ACKNOWLEDGEMENTS
specific failure modes, even when learning entirely via RL
We thank our robot operators for data collection, evalua-
without any intervention data or additional demonstrations.
tions, logistics, and video recording, and our technicians for
VII. DISCUSSIONANDFUTUREWORK robot maintenance and repair. See Appendix A for a full
contributions statement.
Training policies that can achieve the same robustness,
speed, and fluency on real-world tasks as people presents a
REFERENCES
majorchallengeinroboticlearning.Inthispaper,wediscussed
how learning from experience, through a combination of [1] Richard S Sutton and Andrew G Barto. Reinforcement
DAgger-stylecoachingandRL,canbegintoaddressthischal- learning: An introduction. MIT press, 2018. 1
lenge. We describe RECAP, a method for training VLAs with [2] Sascha Lange, Thomas Gabel, and Martin A. Ried-
autonomous trials, reward feedback, and human interventions, miller. Batch reinforcement learning. In Marco A.
and present results for a model trained with RECAP, π∗ , Wiering and Martijn van Otterlo, editors, Reinforce-
0.6
on a set of realistic tasks: making espresso drinks, folding ment Learning, volume 12 of Adaptation, Learning,
diverse laundry, and assembling boxes. At the core of RECAP and Optimization, pages 45–73. Springer, 2012. doi:
is an RL method that is well-suited for scalable training 10.1007/978-3-642-27645-3\ 2. 2, 4
of VLA policies, using advantage conditioning for policy [3] Sergey Levine, Aviral Kumar, George Tucker, and Justin
extraction with value functions. The data for this RL method Fu. Offline reinforcement learning: Tutorial, review,
is collected with a combination of autonomous rollouts and and perspectives on open problems. arXiv preprint
human interventions, correcting mistakes with interventions arXiv:2005.01643, 2020. 2, 4
while finetuning the details of the behavior on autonomous [4] Kevin Frans, Seohong Park, Pieter Abbeel, and Sergey
data.Ourexperimentsshowthat RECAP canimproveboththe Levine. Diffusion guidance is a controllable policy
success rate and throughput of the VLA, more than doubling improvementoperator.arXivpreprint,arXiv:2505.23458,
the throughput on some of the harder tasks, and decreasing 2025. 2, 3, 4, 5, 17
the number of failures by roughly 2×. [5] Kevin Black, Noah Brown, James Darpinian, Karan
There are several directions for improvement with RECAP. Dhabalia, Danny Driess, Adnan Esmail, Michael Robert
First, our system is not fully autonomous: it relies on human Equi, Chelsea Finn, Niccolo Fusai, Manuel Y Galliker,
labeling and effort for reward feedback, interventions, and et al. π : a vision-language-action model with open-
0.5
episode resets. A number of prior works have explored ways worldgeneralization. In9thAnnualConferenceonRobot
to automate these components [84, 85], and VLAs offer Learning, 2025. 2, 3, 5, 7, 8
new ways to provide for more automated data collection, for [6] Physical Intelligence Team. π model card. 2025. 2,
0.6
example by using high-level policies [86] to reason through 5, 6, 8
resetting the scene. Second, our system is relatively na¨ıve in [7] Ste´phane Ross, Geoffrey Gordon, and Drew Bagnell. A
how it approaches exploration: exploration is largely greedy, reduction of imitation learning and structured prediction
relying on stochasticity in the policy and human interventions tono-regretonlinelearning. InAISTATS,pages627–635,
to explore new solutions. This is reasonable when the initial 2011. 2, 7
imitation learning policy already takes reasonable actions, but [8] Michael Laskey, Jonathan Lee, Roy Fox, Anca Dragan,
there is plenty of room for improvement with more sophis- and Ken Goldberg. Shiv: Reducing supervisor burden
ticated exploration methods. Lastly, RECAP performs iterated in dagger using support vectors for efficient learning
“offline” updates (i.e., it collects a batch of data, retrains the fromdemonstrationsinhighdimensionalstatespaces. In
model,andrepeats),ratherthanrunningafullyonlineRLloop Proceedings of the 2016 IEEE International Conference

--- Page 12 ---
on Robotics and Automation (ICRA), pages 462–469, suite for sample-efficient robotic reinforcement learning,
2016. doi: 10.1109/ICRA.2016.7487175. 2 2024.
[9] Michael Laskey, Jonathan Lee, Roy Fox, Anca D. Dra- [20] Lars Ankile, Zhenyu Jiang, Rocky Duan, Guanya Shi,
gan, and Ken Goldberg. Dart: Noise injection for robust Pieter Abbeel, and Anusha Nagabandi. Residual off-
imitation learning. In Proceedings of the 34th Interna- policy rl for finetuning behavior cloning policies. arXiv
tional Conference on Machine Learning (ICML), vol- preprint arXiv:2509.19301, 2025.
ume 70 of Proceedings of Machine Learning Research, [21] Thomas Lampe, Abbas Abdolmaleki, Sarah Bechtle,
pages 1989–1998. PMLR, 2017. Sandy H. Huang, Jost Tobias Springenberg, Michael
[10] Eric Jang, Alex Irpan, Mohi Khansari, Daniel Kappler, Bloesch, Oliver Groth, Roland Hafner, Tim Hertweck,
FrederikEbert,CoreyLynch,SergeyLevine,andChelsea Michael Neunert, Markus Wulfmeier, Jingwei Zhang,
Finn. Bc-z: Zero-shot task generalization with robotic Francesco Nori, Nicolas Heess, and Martin Riedmiller.
imitation learning. In Conference on Robot Learning, Mastering stacking of diverse shapes with large-scale
pages 991–1002. PMLR, 2022. 2 iterative reinforcement learning on real robots. In 2024
[11] Zheyuan Hu, Robyn Wu, Naveen Enock, Jasmine Li, IEEEInternationalConferenceonRoboticsandAutoma-
RiyaKadakia,ZackoryErickson,andAviralKumar.Rac: tion (ICRA), pages 7772–7779, 2024. doi: 10.1109/
Robotlearningforlong-horizontasksbyscalingrecovery ICRA57147.2024.10610297. 2
and correction. arXiv preprint, arXiv:2509.07953, 2025. [22] Perry Dong, Suvir Mirchandani, Dorsa Sadigh, and
2 Chelsea Finn. What matters for batch online re-
[12] Michael Kelly, Chelsea Sidrane, Katherine Driggs- inforcement learning in robotics? arXiv preprint,
Campbell, and Mykel J Kochenderfer. Hg-dagger: Inter- arXiv:2505.08078, 2025. 2
active imitation learning with human experts. In ICRA, [23] Allen Z. Ren, Justin Lidard, Lars Lien Ankile, Anthony
2019. 2 Simeonov, Pulkit Agrawal, Anirudha Majumdar, Ben-
[13] Sergey Levine, Chelsea Finn, Trevor Darrell, and Pieter jamin Burchfiel, Hongkai Dai, and Max Simchowitz.
Abbeel. End-to-endtrainingofdeepvisuomotorpolicies. Diffusion Policy Policy Optimization. In Proceedings
TheJournalofMachineLearningResearch,17(1):1334– of the 2025 International Conference on Learning Rep-
1373, 2016. 2 resentations (ICLR), 2025. 9, 17
[14] Dmitry Kalashnikov, Alex Irpan, Peter Pastor, Julian [24] KunLei,HuanyuLi,DongjieYu,ZhenyuWei,Lingxiao
Ibarz, Alexander Herzog, Eric Jang, Deirdre Quillen, Guo, Zhennan Jiang, Ziyu Wang, Shiyu Liang, and
Ethan Holly, Mrinal Kalakrishnan, Vincent Vanhoucke, Huazhe Xu. Rl-100: Performant robotic manipulation
et al. QT-Opt: Scalable deep reinforcement learning with real-world reinforcement learning. arXiv preprint,
for vision-based robotic manipulation. arXiv preprint arXiv:2510.14830, 2025. 2
arXiv:1806.10293, 2018. [25] Dmitry Kalashnkov, Jake Varley, Yevgen Chebotar, Ben
[15] Ajay Mandlekar, Fabio Ramos, Byron Boots, Li Fei- Swanson, Rico Jonschkowski, Chelsea Finn, Sergey
Fei, Animesh Garg, and Dieter Fox. Iris: Implicit Levine, and Karol Hausman. Mt-opt: Continuous multi-
reinforcement without interaction at scale for learning taskroboticreinforcementlearningatscale. arXiv,2021.
control from offline robot manipulation data. ICRA, 2
2020. [26] AbhishekGupta,JustinYu,TonyZ.Zhao,VikashKumar,
[16] Archit Sharma, M. Ahmed Ahmed Rehaan Ahmad, AaronRovinsky,KelvinXu,ThomasDevlin,andSergey
and Chelsea Finn. Self-improving robots: End-to-end Levine. Reset-free reinforcement learning via multi-
autonomous visuomotor reinforcement learning. In tasklearning:Learningdexterousmanipulationbehaviors
Proceedings of the 7th Conference on Robot Learning without human intervention. In Proceedings of the
(CoRL), volume 229, pages 3292–3308. PMLR, 2023. 2021 IEEE International Conference on Robotics and
[17] Russell Mendonca, Shikhar Bahl, and Deepak Pathak. Automation (ICRA), pages 6664–6671, 2021. 2
Alan: Autonomously exploring robotic agents in the [27] Konstantinos Bousmalis, Giulia Vezzani, Dushyant Rao,
real world. In Proceedings of the 2023 IEEE Interna- ColineDevin,AlexXLee,MariaBauza,TodorDavchev,
tional Conference on Robotics and Automation (ICRA), YuxiangZhou,AgrimGupta,AkhilRaju,etal. Robocat:
pages3044–3050,2023. doi:10.1109/ICRA48891.2023. A self-improving foundation agent for robotic manipula-
10013321. tion. arXiv preprint arXiv:2306.11706, 2023. 2
[18] RussellMendonca,EmmanuelPanov,BernadetteBucher, [28] Aviral Kumar, Anikait Singh, Frederik Ebert, Mitsuhiko
Jiuguang Wang, and Deepak Pathak. Continuously Nakamoto, Yanlai Yang, Chelsea Finn, and Sergey
improving mobile manipulation with autonomous real- Levine. Pre-training for robots: Offline reinforcement
world rl. In Proceedings of the 8th Conference on Robot learning enables learning new tasks from a handful of
Learning (CoRL), pages 5204–5219, 2024. trials. In Proceedings of Robotics: Science and Systems
[19] Jianlan Luo, Zheyuan Hu, Charles Xu, You Liang Tan, (RSS), 2023. doi: 10.15607/RSS.2023.XIX.019.
JacobBerg,ArchitSharma,StefanSchaal,ChelseaFinn, [29] Jingyun Yang, Max Sobol Mark, Brandon Vu, Archit
Abhishek Gupta, and Sergey Levine. Serl: A software Sharma, Jeannette Bohg, and Chelsea Finn. Robot

--- Page 13 ---
fine-tuning made easy: Pre-training rewards and policies Yunfei Ge, Zhenglong Sun, Xiu Li, Chi Zhang, Chenjia
for autonomous real-world reinforcement learning. In Bai, and Xuelong Li. Align-then-steer: Adapting the
Proceedings of the 2024 IEEE International Confer- vision-language action models through unified latent
ence on Robotics and Automation (ICRA), 2024. doi: guidance. arXiv preprint arXiv:2509.02055, 2025. 2
10.1109/ICRA57147.2024.10610421. 2 [41] Andrew Wagenmaker, Mitsuhiko Nakamoto, Yunchu
[30] Shuhan Tan, Kairan Dou, Yue Zhao, and Zhang, Seohong Park, Waleed Yagoub, Anusha Naga-
Philipp Kra¨henbu¨hl. Interactive post-training for bandi,AbhishekGupta,andSergeyLevine.Steeringyour
vision-language-action models. arXiv preprint, diffusionpolicywithlatentspacereinforcementlearning.
arXiv:2505.17016, 2025. 2 InProceedingsofthe9thConferenceonRobotLearning
[31] Guanxing Lu, Wenkai Guo, Chubin Zhang, Yuheng (CoRL), 2025. 2
Zhou,HaonanJiang,ZifengGao,YansongTang,andZi- [42] Charles Xu, Qiyang Li, Jianlan Luo, and Sergey Levine.
weiWang. Vla-rl:Towardsmasterfulandgeneralrobotic Rldg: Robotic generalist policy distillation via reinforce-
manipulationwithscalablereinforcementlearning. arXiv ment learning. arXiv preprint arXiv:2412.09858, 2024.
preprint, arXiv:2505.18719, 2025. 2
[32] JijiaLiu,FengGao,BingwenWei,XinleiChen,Qingmin [43] Dongchi Huang, Zhirui Fang, Tianle Zhang, Yihang
Liao, Yi Wu, Chao Yu, and Yu Wang. What can rl bring Li, Lin Zhao, and Chunhe Xia. Co-rft: Efficient fine-
tovlageneralization?anempiricalstudy. arXivpreprint, tuning of vision-language-action models through chun-
arXiv:2505.19789, 2025. ked offline reinforcement learning. arXiv preprint,
[33] Kang Chen, Zhihao Liu, Tonghe Zhang, Zhen Guo, arXiv:2508.02219, 2025. 3
Si Xu, Hao Lin, Hongzhi Zang, Quanlu Zhang, [44] Zijian Zhang, Kaiyuan Zheng, Zhaorun Chen, Joel
Zhaofei Yu, Guoliang Fan, Tiejun Huang, Yu Wang, Jang, Yi Li, Siwei Han, Chaoqi Wang, Mingyu Ding,
and Chao Yu. π : Online rl fine-tuning for flow- Dieter Fox, and Huaxiu Yao. Grape: Generalizing
rl
based vision-language-action models. arXiv preprint, robot policy via preference alignment. arXiv preprint,
arXiv:2510.25889, 2025. arXiv:2411.19309, 2024. 3
[34] Haozhan Li, Yuxin Zuo, Jiale Yu, Yuhao Zhang, Zhao- [45] Shaopeng Zhai, Qi Zhang, Tianyi Zhang, Fuxian Huang,
hui Yang, Kaiyan Zhang, Xuekai Zhu, Yuchen Zhang, Haoran Zhang, Ming Zhou, Shengzhe Zhang, Litao Liu,
TianxingChen,GanquCui,DehuiWang,DingxiangLuo, Sixu Lin, and Jiangmiao Pang. A vision-language-
Yuchen Fan, Youbang Sun, Jia Zeng, Jiangmiao Pang, action-critic model for robotic real-world reinforcement
ShanghangZhang,YuWang,YaoMu,BowenZhou,and learning. arXiv preprint, arXiv:2509.15937, 2025. 3
Ning Ding. Simplevla-rl: Scaling vla training via rein- [46] Seyed Kamyar Ghasemipour, Ayzaan Wahid, Jonathan
forcement learning. arXiv preprint, arXiv:2509.09674, Tompson, Pannag Sanketi, and Igor Mordatch. Self-
2025. 2 improving embodied foundation models. arXiv preprint,
[35] Yanjiang Guo, Jianke Zhang, Xiaoyu Chen, Xiang Ji, arXiv:2509.15155, 2025. 3
Yen-JenWang,YuchengHu,andJianyuChen.Improving [47] Ju¨rgen Schmidhuber. Reinforcement learning upside
vision-language-action model with online reinforcement down:Don’tpredictrewards—justmapthemtoactions.
learning. arXiv preprint, arXiv:2501.16664, 2025. 2 arXiv preprint, arXiv:1912.02875, 2019. 3, 4
[36] WenliXiao,HaotianLin,AndyPeng,HaoruXue,Tairan [48] Aviral Kumar, Xue Bin Peng, and Sergey Levine.
He, Yuqi Xie, Fengyuan Hu, Jimmy Wu, Zhengyi Luo, Reward-conditioned policies. CoRR, abs/1912.13465,
Linxi ”Jim” Fan, Guanya Shi, and Yuke Zhu. Self- 2019. 4
improving vision-language-action models with data gen- [49] Lili Chen, Kevin Lu, Aravind Rajeswaran, Kimin Lee,
eration via residual rl, 2025. 2 Aditya Grover, Michael Laskin, Pieter Abbeel, Aravind
[37] Yuhui Chen, Shuai Tian, Shugao Liu, Yingting Zhou, Srinivas,andIgorMordatch. Decisiontransformer:Rein-
Haoran Li, and Dongbin Zhao. Conrft: A reinforced forcement learning via sequence modeling. In Advances
fine-tuningmethodforvlamodelsviaconsistencypolicy. inNeuralInformationProcessingSystems(NeurIPS)34,
arXiv preprint arXiv:2502.05450, 2025. 2 2021.
[38] Max Sobol Mark, Tian Gao, Georgia Gabriela Sampaio, [50] David Brandfonbrener, Alberto Bietti, Jacob Buckman,
Mohan Kumar Srirama, Archit Sharma, Chelsea Finn, Romain Laroche, and Joan Bruna. When does return-
and Aviral Kumar. Policy-agnostic rl: Offline rl and conditioned supervised learning work for offline rein-
online rl fine-tuning of any class and backbone. arXiv forcement learning? In Advances in Neural Information
preprint, arXiv:2412.06685, 2024. 2 Processing Systems (NeurIPS) 35, 2022. 4
[39] Mitsuhiko Nakamoto, Oier Mees, Aviral Kumar, and [51] ScottEmmons,BenjaminEysenbach,IlyaKostrikov,and
Sergey Levine. Steering your generalists: Improving Sergey Levine. Rvs: What is essential for offline rl
robotic foundation models via value guidance. In Con- via supervised learning? In Proceedings of the 10th
ference on Robot Learning, pages 4996–5013. PMLR, International Conference on Learning Representations
2025. (ICLR), 2022.
[40] Yang Zhang, Chenwei Wang, Ouyang Lu, Yuan Zhao, [52] Hiroki Furuta, Yusuke Matsuo, and Shixiang Shane Gu.

--- Page 14 ---
Generalized decision transformer for offline hindsight Sontakke, Joseph J. Lim, Jesse Thomason, Erdem Bıyık,
information matching. In Proceedings of the 10th and Jesse Zhang. Rewind: Language-guided rewards
International Conference on Learning Representations teach robot policies without new demonstrations. In
(ICLR), 2022. Proceedings of the 9th Conference on Robot Learning
[53] Taku Yamagata, Ahmed Khalil, and Rau´l Santos- (CoRL), 2025.
Rodr´ıguez. Q-learning decision transformer: Leveraging [63] Minttu Alakuijala, Reginald McLean, Isaac Woungang,
dynamic programming for conditional sequence mod- Nariman Farsad, Samuel Kaski, Pekka Marttinen, and
elling in offline rl. In Proceedings of the 40th Interna- Kai Yuan. Video-language critic: Transferable reward
tionalConferenceonMachineLearning(ICML),volume functions for language-conditioned robotics. Transac-
202ofProceedingsofMachineLearningResearch,pages tions on Machine Learning Research, 2025:1–22, 2025.
38989–39007. PMLR, 2023. 3
[54] Qinqing Zheng, Amy Zhang, and Aditya Grover. Online [64] YechengJasonMa,WilliamLiang,VaidehiSom,Vikash
decisiontransformer. InProceedingsofthe39thInterna- Kumar, Amy Zhang, Osbert Bastani, and Dinesh Jayara-
tionalConferenceonMachineLearning(ICML),volume man. Liv: Language-image representations and rewards
162ofProceedingsofMachineLearningResearch,pages for robotic control. In Proceedings of the 40th Interna-
27042–27059. PMLR, 2022. tional Conference on Machine Learning (ICML), 2023.
[55] JakubGrudzienKuba,PieterAbbeel,andSergeyLevine. 3
Advantage-conditioned diffusion: Offline rl via general- [65] Yecheng Jason Ma, Joey Hejna, Chuyuan Fu, Dhruv
ization. 2023. Shah, Jacky Liang, Zhuo Xu, Sean Kirmani, Peng Xu,
[56] Yueh-Hua Wu, Xiaolong Wang, and Masashi Hamaya. Danny Driess, Ted Xiao, Osbert Bastani, Dinesh Ja-
Elastic decision transformer. In Proceedings of the 37th yaraman, Wenhao Yu, Tingnan Zhang, Dorsa Sadigh,
Conference on Neural Information Processing Systems and Fei Xia. Vision language models are in-context
(NeurIPS), 2023. doi: 10.5555/3666122.3666936. 3 value learners. In Proceedings of the 13th International
[57] LinShao,TokiMigimatsu,QiangZhang,KaiyuanYang, Conference on Learning Representations (ICLR), 2025.
and Jeannette Bohg. Concept2robot: Learning manipu- 3
lation concepts from instructions and human demonstra- [66] John Schulman, Filip Wolski, Prafulla Dhariwal, Alec
tions. In Proceedings of Robotics: Science & Systems Radford,andOlegKlimov. Proximalpolicyoptimization
(RSS), 2020. doi: 10.15607/RSS.2020.XVI.082. 3 algorithms. arXiv preprint arXiv:1707.06347, 2017. 3,
[58] Annie S. Chen, Suraj Nair, and Chelsea Finn. Learn- 4, 17
ing generalizable robotic reward functions from “in-the- [67] Abbas Abdolmaleki, Jost Tobias Springenberg, Yuval
wild”humanvideos.InProceedingsofRobotics:Science Tassa, Remi Munos, Nicolas Heess, and Martin Ried-
& Systems (RSS) 2021, 2021. miller. Maximum a posteriori policy optimisation. In
[59] Suraj Nair, Eric Mitchell, Kevin Chen, Brian Ichter, International Conference on Learning Representations,
Silvio Savarese, and Chelsea Finn. Learning language- 2018. 3
conditioned robot behavior from offline data and crowd- [68] Xue Bin Peng, Aviral Kumar, Grace Zhang, and Sergey
sourcedannotation. InProceedingsofthe5thConference Levine. Advantage-weighted regression: Simple and
on Robot Learning (CoRL), volume 164 of Proceed- scalableoff-policyreinforcementlearning.arXivpreprint
ings of Machine Learning Research, pages 1303–1315. arXiv:1910.00177, 2019. 4, 9
PMLR, 2022. [69] PeterDayanandGeoffreyE.Hinton. Usingexpectation-
[60] Sumedh A. Sontakke, Jesse Zhang, Se´bastien M.R. maximization for reinforcement learning. Neural Com-
Arnold, Karl Pertsch, Erdem Bıyık, Dorsa Sadigh, putation,9(2):271–278,1997. doi:10.1162/neco.1997.9.
Chelsea Finn, and Laurent Itti. Roboclip: One demon- 2.271.
strationisenoughtolearnrobotpolicies. InProceedings [70] Jan Peters, Katharina Mu¨lling, and Yasemin Altu¨n. Rel-
ofthe37thConferenceonNeuralInformationProcessing ative entropy policy search. In Proceedings of the
Systems (NeurIPS), 2023. Twenty-Fourth AAAI Conference on Artificial Intelli-
[61] Wenhao Yu, Nimrod Gileadi, Chuyuan Fu, Sean Kir- gence, AAAI’10, page 1607–1612. AAAI Press, 2010.
mani, Kuang-Huei Lee, Montse Gonzalez Arenas, Hao- 3
Tien Lewis Chiang, Tom Erez, Leonard Hasenclever, [71] Qing Wang, Jiechao Xiong, Lei Han, peng sun, Han
Jan Humplik, Brian Ichter, Ted Xiao, Peng Xu, Andy Liu, and Tong Zhang. Exponentially weighted imitation
Zeng, Tingnan Zhang, Nicolas Heess, Dorsa Sadigh, Jie learningforbatchedhistoricaldata.InS.Bengio,H.Wal-
Tan, Yuval Tassa, and Fei Xia. Language to rewards lach, H. Larochelle, K. Grauman, N. Cesa-Bianchi, and
for robotic skill synthesis. In Proceedings of the 7th R. Garnett, editors, Advances in Neural Information
Conference on Robot Learning (CoRL), volume 229 of Processing Systems, volume 31, 2018. 3
Proceedings of Machine Learning Research, pages 374– [72] Marc G Bellemare, Will Dabney, and Re´mi Munos.
404. PMLR, 2023. A distributional perspective on reinforcement learning.
[62] Jiahui Zhang, Yusen Luo, Abrar Anwar, Sumedh Anand In International conference on machine learning, pages

--- Page 15 ---
449–458. PMLR, 2017. 4 erick Liu, Gagik Amirkhanyan, Glenn Cameron, Hadi
[73] Danny Driess, Jost Tobias Springenberg, Brian Ichter, Hashemi, Hanna Klimczak-Plucin´ska, Harman Singh,
Lili Yu, Adrian Li-Bell, Karl Pertsch, Allen Z Ren, Harsh Mehta, Harshal Tushar Lehri, Hussein Hazimeh,
Homer Walke, Quan Vuong, Lucy Xiaoyang Shi, et al. IanBallantyne,IdanSzpektor,IvanNardini,JeanPouget-
Knowledge insulating vision-language-action models: Abadie,JethaChan,JoeStanton,JohnWieting,Jonathan
Train fast, run fast, generalize better. In Proceedings of Lai, Jordi Orbay, Joseph Fernandez, Josh Newlan,
the 37th Conference on Neural Information Processing JuyeongJi,JyotinderSingh,KatBlack,KathyYu,Kevin
Systems (NeurIPS), 2025. 4, 6 Hui,KiranVodrahalli,KlausGreff,LinhaiQiu,Marcella
[74] Tuomas Haarnoja, Aurick Zhou, Pieter Abbeel, and Valentine, Marina Coelho, Marvin Ritter, Matt Hoffman,
Sergey Levine. Soft actor-critic: Off-policy maximum Matthew Watson, Mayank Chaturvedi, Michael Moyni-
entropy deep reinforcement learning with a stochastic han, Min Ma, Nabila Babar, Natasha Noy, Nathan Byrd,
actor. ICML, 2018. 4 Nick Roy, Nikola Momchev, Nilay Chauhan, Noveen
[75] Ziyu Wang, Alexander Novikov, Konrad Zolna, Josh S Sachdeva, Oskar Bunyan, Pankil Botarda, Paul Caron,
Merel, Jost Tobias Springenberg, Scott E Reed, Bobak Paul Kishan Rubenstein, Phil Culliton, Philipp Schmid,
Shahriari, Noah Siegel, Caglar Gulcehre, Nicolas Heess, PierGiuseppeSessa,PingmeiXu,PiotrStanczyk,Pouya
and Nando de Freitas. Critic regularized regression. In Tafti, Rakesh Shivanna, Renjie Wu, Renke Pan, Reza
H. Larochelle, M. Ranzato, R. Hadsell, M.F. Balcan, Rokni, Rob Willoughby, Rohith Vallu, Ryan Mullins,
and H. Lin, editors, Advances in Neural Information SammyJerome,SaraSmoot,SertanGirgin,ShariqIqbal,
ProcessingSystems,volume33,pages7768–7778,2020. Shashir Reddy, Shruti Sheth, Siim Po˜der, Sijal Bhat-
4 nagar, Sindhu Raghuram Panyam, Sivan Eiger, Susan
[76] Ilya Kostrikov, Ashvin Nair, and Sergey Levine. Offline Zhang,TianqiLiu,TrevorYacovone,TylerLiechty,Uday
reinforcementlearningwithimplicitq-learning. InInter- Kalra, Utku Evci, Vedant Misra, Vincent Roseberry,
national Conference on Learning Representations, 2022. VladFeinberg,VladKolesnikov,WoohyunHan,Woosuk
4 Kwon, Xi Chen, Yinlam Chow, Yuvein Zhu, Zichuan
[77] Karl Pertsch, Kyle Stachowicz, Brian Ichter, Danny Wei, Zoltan Egyed, Victor Cotruta, Minh Giang, Phoebe
Driess, Suraj Nair, Quan Vuong, Oier Mees, Chelsea Kirk, Anand Rao, Kat Black, Nabila Babar, Jessica Lo,
Finn, and Sergey Levine. FAST: Efficient action tok- Erica Moreira, Luiz Gustavo Martins, Omar Sanseviero,
enization for vision-language-action models. Robotics: Lucas Gonzalez, Zach Gleicher, Tris Warkentin, Vahab
Science and Systems, 2025. 6 Mirrokni,EvanSenter,EliCollins,JoelleBarral,Zoubin
[78] Gemma Team, Aishwarya Kamath, Johan Ferret, Shreya Ghahramani,RaiaHadsell,YossiMatias,D.Sculley,Slav
Pathak, Nino Vieillard, Ramona Merhej, Sarah Per- Petrov, Noah Fiedel, Noam Shazeer, Oriol Vinyals, Jeff
rin, Tatiana Matejovicova, Alexandre Rame´, Morgane Dean, Demis Hassabis, Koray Kavukcuoglu, Clement
Rivie`re, Louis Rouillard, Thomas Mesnard, Geoffrey Farabet, Elena Buchatskaya, Jean-Baptiste Alayrac, Ro-
Cideron, Jean bastien Grill, Sabela Ramos, Edouard han Anil, Dmitry, Lepikhin, Sebastian Borgeaud, Olivier
Yvinec, Michelle Casbon, Etienne Pot, Ivo Penchev, Bachem,ArmandJoulin,AlekAndreev,CassidyHardin,
Gae¨l Liu, Francesco Visin, Kathleen Kenealy, Lucas Robert Dadashi, and Le´onard Hussenot. Gemma 3
Beyer, Xiaohai Zhai, Anton Tsitsulin, Robert Busa- technical report, 2025. 6
Fekete, Alex Feng, Noveen Sachdeva, Benjamin Cole- [79] YaronLipman,RickyTQChen,HeliBen-Hamu,Maxim-
man, Yi Gao, Basil Mustafa, Iain Barr, Emilio Parisotto, ilian Nickel, and Matt Le. Flow matching for generative
David Tian, Matan Eyal, Colin Cherry, Jan-Thorsten modeling. arXiv preprint arXiv:2210.02747, 2022. 6, 16
Peter, Danila Sinopalnikov, Surya Bhupatiraju, Rishabh [80] Diederik Kingma and Ruiqi Gao. Understanding diffu-
Agarwal, Mehran Kazemi, Dan Malkin, Ravin Ku- sion objectives as the elbo with simple data augmenta-
mar, David Vilar, Idan Brusilovsky, Jiaming Luo, An- tion. In A. Oh, T. Naumann, A. Globerson, K. Saenko,
dreas Steiner, Abe Friesen, Abhanshu Sharma, Abheesht M.Hardt,andS.Levine,editors,AdvancesinNeuralIn-
Sharma, Adi Mayrav Gilady, Adrian Goedeckemeyer, formationProcessingSystems,volume36,pages65484–
Alaa Saade, Alex Feng, Alexander Kolesnikov, Alexei 65516, 2023. 6, 16
Bendebury, Alvin Abdagic, Amit Vadi, Andra´s Gyo¨rgy, [81] Kevin Black, Noah Brown, Danny Driess, Adnan Es-
Andre´ Susano Pinto, Anil Das, Ankur Bapna, An- mail, Michael Equi, Chelsea Finn, Niccolo Fusai,
toine Miech, Antoine Yang, Antonia Paterson, Ashish Lachy Groom, Karol Hausman, Brian Ichter, Szymon
Shenoy, Ayan Chakrabarti, Bilal Piot, Bo Wu, Bobak Jakubczak, Tim Jones, Liyiming Ke, Sergey Levine,
Shahriari, Bryce Petrini, Charlie Chen, Charline Le Adrian Li-Bell, Mohith Mothukuri, Suraj Nair, Karl
Lan, Christopher A. Choquette-Choo, CJ Carey, Cormac Pertsch,LucyXiaoyangShi,JamesTanner,QuanVuong,
Brick, Daniel Deutsch, Danielle Eisenbud, Dee Cattle, Anna Walling, Haohuan Wang, and Ury Zhilinsky. π :
0
Derek Cheng, Dimitris Paparas, Divyashree Shivakumar A vision-language-action flow model for general robot
Sreepathihalli, Doug Reid, Dustin Tran, Dustin Zelle, control. arXiv preprint arXiv:2410.24164, 2024. 8
EricNoland,ErwinHuizenga,EugeneKharitonov,Fred- [82] David McAllister, Songwei Ge, Brent Yi, Chung Min

--- Page 16 ---
Kim, Ethan Weber, Hongsuk Choi, Haiwen Feng, and Brian Ichter, Liyiming Ke, Sergey Levine, Suraj Nair, Allen
Angjoo Kanazawa. Flow matching policy gradients, Z.Ren,LauraSmith,JostTobiasSpringenberg,ZhiyuanZhou
2025. 9, 16, 17
B. Additional Value Function Visualization
[83] Zhengpeng Xie, Qiang Zhang, Fan Yang, Marco Hutter,
Figure 13 shows additional visualizations of our trained
and Renjing Xu. Simple policy optimization. In Forty-
valuefunctiononfivedifferenttasks,includingtasksonwhich
second International Conference on Machine Learning
weevaluateourpolicies(espressomaking,boxassembly)and
(ICML), 2025. 9, 17
also broader tasks (hang towel, attach hook). The parts with
[84] Henry Zhu, Justin Yu, Abhishek Gupta, Dhruv Shah,
the most prominent changes are highlighted: red corresponds
Kristian Hartikainen, Avi Singh, Vikash Kumar, and
to where value function drops, green corresponds to where
Sergey Levine. The ingredients of real-world robotic re-
valuefunctionincreases,andyellowcorrespondstooscillating
inforcement learning. arXiv preprint arXiv:2004.12570,
values.Imagesshowthecorrespondingframesanddescription
2020. 11
of the episode.
[85] Archit Sharma, Kelvin Xu, Nikhil Sardana, Abhishek
Gupta, Karol Hausman, Sergey Levine, and Chelsea C. Computing the log-likelihood for policy improvement
Finn. Autonomous reinforcement learning: Formalism To derive the log-likelihood from Equation (4) we can first
and benchmarking. arXiv preprint arXiv:2112.09605, observe that we can decompose the full model likelihood into
2021. 11 autoregressive and diffusion terms
[86] Lucy Xiaoyang Shi, Brian Ichter, Michael Equi, Liy-
π (a ,aℓ ,ℓˆ|I ,o ,ℓ)=
iming Ke, Karl Pertsch, Quan Vuong, James Tanner, θ t:t+H t:t+H t t
Anna Walling, Haohuan Wang, Niccolo Fusai, et al. π (a |I ,o ,ℓ,ℓˆ)π (aℓ |I ,o ,ℓ,ℓˆ)π (ℓˆ|I ,o ,ℓ),
θ t:t+H t t θ t:t+H t t θ t t
Hi robot: Open-ended instruction following with hier- (6)
archical vision-language-action models. arXiv preprint wherethefirsttermismodeledwithflowmatching,thesecond
arXiv:2502.19417, 2025. 11 term is the autoregressive likelihood of the discretized actions
aℓ , and the third term corresponds to the autoregressive
t:t+H
APPENDIX text likelihood. The autoregressive likelihoods can be esti-
matedintheusualway,usingthecross-entropylossevaluated
A. Contributions
on ground truth tokens. For the continuous likelihood over
Data collectionand operations.MichaelEqui,ChelseaFinn, a , a closed form likelihood is not available [79]. We
t:t+H
Lachy Groom, Hunter Hancock, Karol Hausman, Rowan Jen, can,howeverfollowpriorwork[82],andconsidertheone-step
LiyimingKe,MarindaLamb,VishnuMano,SurajNair,Charvi diffusion process as a Gaussian distribution with likelihood
Sharma, Laura Smith, Will Stoeckle, Anna Walling, Blake logπ (a |aη,ω,I ,o ,ℓ,ℓˆ)=
Williams. θ t:t+H 1:H t t
(cid:16) (cid:17) (7)
Annotationandsupplementaldata.ChelseaFinn,Catherine logN ω−f θ (aη 1: , H ω,I t ,o t ,ℓ,ℓˆ),I ,
Glossop, Hunter Hancock, Brian Ichter, Rowan Jen, Liyiming
with aη,ω = ηa +(1−η)ω and ω = N(0,I). From
Ke,ChandraKuchi,KarlPertsch,LauraSmith,WillStoeckle, t:t+H t:t+H
this we can form an evidence lower bound to the likelihood
Quan Vuong, Anna Walling.
following [80, 82] (effectively marginalizing over η and ω)
Policy training and research. Ashwin Balakrishna, Kevin
which yields
Black, Danny Driess, Michael Equi, Yunhao Fang, Chelsea
Finn, Catherine Glossop, Karol Hausman, Gashon Hussein, logπ θ (a t:t+H |I t ,o t ,ℓ,ℓˆ)≥
Brian Ichter, Liyiming Ke, Sergey Levine, Yao Lu, Suraj 1 (cid:104) (cid:13) (cid:13)2(cid:105)
E −w(η)(cid:13)ω−a −f (aη,ω,I ,o ,ℓ,ℓˆ)(cid:13) +c,
Nair, Karl Pertsch, Allen Z. Ren, Lucy Shi, Laura Smith, 2 η,ω (cid:13) 1:H θ 1:H t t (cid:13)
(8)
Jost Tobias Springenberg, Kyle Stachowicz, Alex Swerdlow,
where w(η) = e−η/2 is a noise dependent weighting term,
Marcel Torne, Quan Vuong, Lili Yu, Zhiyuan Zhou.
and c is a constant independent of f . For the derivation,
Policy infrastructure. Kevin Black, Karan Dhabalia, Danny θ
see [80], which also derives the relationship between flow
Driess,MichaelEqui,LiyimingKe,AdrianLi-Bell,SurajNair,
matching and diffusion in Appendix D.3 for this choice of
Allen Z. Ren, Laura Smith, Jost Tobias Springenberg, Kyle
weighting term. Finally putting the lower bound together with
Stachowicz, Alex Swerdlow, Haohuan Wang, Ury Zhilinsky,
the autoregressive likelihood for the discretized action part of
Zhiyuan Zhou.
the text output ℓˆ, and subsuming the weighting terms in α,
Robot hardware. Ali Amin, Raichelle Aniceto, Grace Con-
gives
nors, Adnan Esmail, Thomas Godden, Ivan Goryachev, Tim
Jones, Ben Katz, Devin LeBlanc, Mohith Mothukuri, Sukwon logπ (a ,aℓ |I ,o ,ℓ,ℓˆ)≥
θ t:t+H t:t+H t t
Yoo. (cid:104)
E logp (aℓ |I ,o ,ℓ,ℓˆ)
Robot infrastructure. Ken Conley, James Darpinian, Jared η,ω θ t:t+H t t (9)
DiCarlo, Karol Hausman, Szymon Jakubczak, James Tanner. (cid:13) (cid:13)2(cid:105)
−α (cid:13)ω−a −f (aη,ω,I ,o ,ℓ,ℓˆ)(cid:13) ,
Writing and illustration. Kevin Black, Danny Driess, η(cid:13) 1:H θ 1:H t t (cid:13)
MichaelEqui,ChelseaFinn,HunterHancock,KarolHausman, which is the bound given in the main part of the paper.

--- Page 17 ---
can be written as
logπ (a ,aℓ |o ,ℓ,ℓˆ)≥
θ t:t+H t:t+H t
(cid:104)
Drops portafilter multiple times Succeeds & continues E logp (aℓ |o ,ℓ,ℓˆ)
η,ω θ t:t+H t (10)
(cid:13) (cid:13)2(cid:105)
−α (cid:13)ω−a −f (aη,ω,o ,ℓ,ℓˆ)(cid:13) ,
η(cid:13) 1:H θ 1:H t (cid:13)
which is analogous to the diffusion likelihood bound used in
FPO[82].AndwecombineitwithaPPOstylelossseparated
into diffusion and autoregressive terms. In preliminary exper-
iments we found that for our setting it was difficult to enforce
a trust region constraint on the action expert (which models
Successfully building a cardboard box actions with an unbounded diffusion head) when using the
standard PPO clipping objective. Presumably, this is partially
due to the “offline” nature of our algorithm setting, where
we cannot afford to collect new data from real robots every
few gradient steps. To stabilize training we found using an
alternativedefinitionofthePPOconstraintfollowingSPO[83]
to be effective. The resulting loss is given as:
L (θ)=
SPO+CoVLA
(cid:40)
π (a ∈ℓˆ|o ,ℓ)
Right arm drops towel Tidy Successfully hangs towel
π
θ
(a
ℓˆ
∈ℓˆ|o
t
,ℓ)
Aπref(o
t
,a
t
,ℓ)
ref ℓˆ t
(cid:34) (cid:35)(cid:41)
−
|Aπref(o
t
,a
t
,ℓ)| π
θ
(a
ℓˆ
∈ℓˆ|o
t
,ℓ)
−1
2ϵ ar π ref (a ℓˆ ∈ℓˆ|o t ,ℓ) (11)
(cid:40)
π (a |o ,ℓ)
+α
π
θ
(a
t:t+H
|o
t
,ℓ)
Aπref(o
t
,a
t
,ℓ)
ref t:t+H t
(cid:34) (cid:35)(cid:41)
−
|Aπref(o
t
,a
t
,ℓ)| π
θ
(a
t:t+H
|o
t
,ℓ)
−1 ,
2ϵ π (a |o ,ℓ)
Tries to attach the hook but the hook flies off due to unstable hold flow ref t:t+H t
where α is a trade-off parameter and ϵ , ϵ are trust-region
ar flow
parameters for autoregressive and flow-matching model parts
respectively. We use this variant to perform training on eval
data starting from the π checkpoint.
0.6
E. Using CFG for test-time policy improvement with β >1
Fig.13:Additionalvisualizationofvaluefunctiononfivedifferenttasks. After training we can choose to further sharpen the policy
Red parts highlight places where value drops, green parts highlight places used for evaluation by setting β >1 in Eq. (2). As shown in
where value increases, and yellow parts highlight oscillating value regions.
prior work [4] we can recover this sharpened policy without
Imagesshowthecorrespondingframesanddescriptionsoftheepisode.
additional training since it is implicitly defined by the learned
policiesπ (a |I ,o ,ℓ)andπ (a |o ,ℓ).Specifically,
θ t:t+H t t θ t:t+H t
after training we can form the approximation
D. PPO implementation (cid:18)
π (a |I ,o ,ℓ)
(cid:19)β
πˆ(a |o ,ℓ)∝π (a |o ,ℓ) ref t:t+H t t .
t:t+H t ref t:t+H t π (a |o ,ℓ)
ref t:t+H t
(12)
We implement a variant of PPO [66] related to DPPO and
One can now realize that the diffusion model effectively
FPO[23,82]anduseitasanadditionalbaseline.Toallowfor
learns the gradient of the likelihoods, i.e. it represents
trainingboththeautoregressivepartofthemodelaswellasthe
∇ logπ (a |I ,o ,ℓ) and ∇ logπ (a |o ,ℓ) re-
diffusion based action expert in a compute effective manner a θ t:t+H t t a θ t:t+H t
spectively. From this, following Frans et al. [4], we can see
we calculate likelihoods based on the single step diffusion
that if we run flow-matching inference following the gradient
objective alone.
In particular, we use a likelihood bound analogous to Eq. ∇ a logπ θ (a t:t+H |o t ,ℓ)+
(9) (previous section) but without the improvement indicator. β(∇ logπ (a |I ,o ,ℓ)−∇ logπ (a |o ,ℓ)),
a θ t:t+H t t a θ t:t+H t
Decomposingintoautoregressiveandflow-matchingtermsthis (13)

--- Page 18 ---
we are effectively sampling from the desired attenuated dis- without expert corrections. As we push model performance to
tribution. We note that, as mentioned in the main paper, the closely resemble the expert data collector in terms of speed,
parameter β is loosely connected to the advantage threshold it becomes hard to provide corrections. For this task, We
ϵ that we introduce during training (in the sense that both collect 300 episodes across 4 robot stations for reporting eval
ℓ
sharpen the distribution, one at inference and one at training performance. For the diverse laundry folding task we collect
time). We find that sharpening the distribution after training 450 evaluation episodes and 287 correction episodes. For the
withhighsettingsforβ canleadtopushingtheactiondistribu- failuremoderemovalablationwecollectbothautonomousand
tion towards the boundaries of its learned support (which can policycorrectiondata.Intotalwecollect∼1000autonomous
leadtooverlyaggressivemotions)andthusprimarilyrelyonϵ and 280+378 correction episodes spread over 3 robots. For
ℓ
for obtaining a good conditioned policy directly after training box assembly we collect data in the deployment scenario
and combine it with moderate settings (e.g. β ∈ [1.5,2.5]) directly, collecting 600 demonstrations and 360 correction
where useful. episodes in each iteration, using 3 robots in total. For cafe we
perform a single iteration and collect 429 correction episodes
F. Additional algorithm details
as well as 414 autonomous episodes.
We describe details for setting the task specific parameters
used in Algorithm 1.
Advantage Estimation: During post-training, we estimate
the advantage function using Aπ(o ,a ) = (cid:80)t+N−1r′ +
t t t′=t t
Vπ(o )−Vπ(o ), where o is an observation sampled
t+N t t+N
fromN stepsaheadfromthesametrajectory.WeuseN =50
lookaheadtocalculatethisadvantage.Duringpre-training,we
calculate the advantage estimate as Aπ(o ,a ) = (cid:80)T r′ −
t t t′=0 t
Vπ(o ), setting N = T for each episode, which is a higher
t
variance estimate of the advantage. We use this advantage
calculationsinceitallowsustocalculatetheadvantagevalues
on-the-fly during pre-training using a single inference call to
the value function. We find empirically that this advantage
estimate works well when the policy is trained on large
amounts of data from diverse tasks during pre-training.
Advantage conditioning dropout: During training, we
randomly drop out the conditioning on the advantage indi-
cator 30% of the time. We employ this dropout so that we
can directly sample directly from either the conditional or
unconditional policy during inference time and use CFG for
test-time policy improvement (see Section E for details); and
it effectively replaces the loss multiplier α.
Advantage threshold: The per task advantage threshold ϵ
ℓ
is set as follows. During pre-training we select the threshold
for each task such that approximately 30% of the demonstra-
tion data has positive advantage (as calculatedd on a random
sampleof10kdatapoints).Duringfine-tuningwegenerallyset
the threshold such that approximately 40% of the evaluation
rollouts in each iteration have positive advantage. For the T-
shirt and shorts laundry folding task (in which training on
high-quality demonstration data yields slow policies but with
high success rate) we increase the threshold such that only
approximately 10% of the data has positive advantage.
Dataset composition:Weusethedatasetaggregationstrat-
egy described in Algorithm 1 for all tasks. However each
of our task has distinct nature: the episode lengths vary, the
performances of Iteration 0 model on each task are differ-
ent, and one task (Assemble Box) is performed offsite in a
deployment scenario. Therefore, we have different amount of
demonstrationdatatobeginwithandcollectdifferentamounts
of experience data for iterative improvement. For laundry (T-
shirt and shorts), we use autonomous evaluation data only