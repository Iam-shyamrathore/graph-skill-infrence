

DeepPath: A Reinforcement Learning Method for
## Knowledge Graph Reasoning
Wenhan XiongandThien HoangandWilliam Yang Wang
Department of Computer Science
University of California, Santa Barbara
Santa Barbara, CA 93106 USA
{xwhan,william}@cs.ucsb.edu, thienhoang@umail.ucsb.edu
## Abstract
We study the problem of learning to reason
in  large  scale  knowledge  graphs  (KGs).
More specifically, we describe a novel re-
inforcement learning framework for learn-
ing  multi-hop  relational  paths:  we  use  a
policy-based agent with continuous states
based  on  knowledge  graph  embeddings,
which  reasons  in  a  KG  vector  space  by
sampling  the  most  promising  relation  to
extend its path.  In contrast to prior work,
our  approach  includes  a  reward  function
that takes theaccuracy,diversity, andef-
ficiencyinto  consideration.   Experimen-
tally,  we show that our proposed method
outperforms  a  path-ranking  based  algo-
rithm  and  knowledge  graph  embedding
methods  on  Freebase  and  Never-Ending
Language Learning datasets.
## 1
## 1    Introduction
Deep  neural  networks  for  acoustic  modeling  in
speech  recognitionIn  recent  years,   deep  learn-
ing  techniques  have  obtained  many  state-of-the-
art results in various classification and recognition
problems (Krizhevsky et al., 2012; Hinton et al.,
2012; Kim, 2014). However, complex natural lan-
guage  processing  problems  often  require  multi-
ple inter-related decisions, and empowering deep
learning models with the ability of learning to rea-
son  is  still  a  challenging  issue.   To  handle  com-
plex queries where there are no obvious answers,
intelligent machines must be able to reason with
existing resources, and learn to infer an unknown
answer.
More  specifically,  we  situate  our  study  in  the
context of multi-hop reasoning, which is the task
## 1
Code and the NELL dataset are available athttps://
github.com/xwhan/DeepPath.
of  learning  explicit  inference  formulas,  given  a
large  KG.  For  example,  if  the  KG  includes  the
beliefs such asNeymarplays forBarcelona, and
Barcelonaare  in  theLa  Ligaleague,  then  ma-
chines should be able to learn the following for-
mula:playerPlaysForTeam(P,T)∧teamPlaysIn-
League(T,L)⇒playerPlaysInLeague(P,L). In the
testing time, by plugging in the learned formulas,
the system  should be  able to  automatically  infer
the missing link between a pair of entities.  This
kind of reasoning machine will potentially serve
as  an  essential  components  of  complex  QA  sys-
tems.
In  recent  years,  the  Path-Ranking  Algorithm
(PRA)  (Lao  et  al.,  2010,  2011a)  emerges  as  a
promising method for learning inference paths in
large KGs. PRA uses a random-walk with restarts
based  inference  mechanism  to  perform  multiple
bounded depth-first search processes to find rela-
tional paths. Coupled with elastic-net based learn-
ing,  PRA  then  picks  more  plausible  paths  using
supervised  learning.   However,  PRA  operates  in
a fully discrete space, which makes it difficult to
evaluate and compare similar entities and relations
in a KG.
In  this  work,  we  propose  a  novel  approach
for  controllable  multi-hop  reasoning:   we  frame
the path learning process as reinforcement learn-
ing (RL). In contrast to PRA, we use translation-
based knowledge based embedding method (Bor-
des et al., 2013) to encode the continuous state of
our RL agent,  which reasons in the vector space
environment of the knowledge graph.  The agent
takes incremental steps by sampling a relation to
extend its path.  To better guide the RL agent for
learning  relational  paths,  we  use  policy  gradient
training (Mnih et al., 2015) with a novel reward
function  that  jointly  encourages  accuracy,  diver-
sity, and efficiency. Empirically, we show that our
method  outperforms  PRA  and  embedding  based
arXiv:1707.06690v3  [cs.CL]  7 Jul 2018

methods on a Freebase and a Never-Ending Lan-
guage  Learning  (Carlson  et  al.,  2010a)  dataset.
Our contributions are three-fold:
•We  are  the  first  to  consider  reinforcement
learning (RL) methods for learning relational
paths in knowledge graphs;
•Our learning method uses a complex reward
function  that  considers  accuracy,  efficiency,
and  path  diversity  simultaneously,  offering
better control and more flexibility in the path-
finding process;
•We  show  that  our  method  can  scale  up  to
large  scale  knowledge  graphs,  outperform-
ing PRA and KG embedding methods in two
tasks.
In  the  next  section,  we  outline  related  work  in
path-finding and embedding methods in KGs. We
describe  the  proposed  method  in  Section  3.   We
show  experimental results  in  Section  4.   Finally,
we conclude in Section 5.
## 2    Related Work
The Path-Ranking Algorithm (PRA) method (Lao
et al., 2011b) is a primary path-finding approach
that uses random walk with restart strategies for
multi-hop reasoning.  Gardner et al. (2013; 2014)
propose a modification to PRA that computes fea-
ture  similarity  in  the  vector  space.Wang  and
Cohen (2015) introduce a recursive random walk
approach for integrating the background KG and
text—the  method  performs  structure  learning  of
logic  programs  and  information  extraction  from
text at the same time.  A potential bottleneck for
random walk inference is that supernodes connect-
ing to large amount of formulas will create huge
fan-out areas that significantly slow down the in-
ference and affect the accuracy.
Toutanova et al. (2015) provide a convolutional
neural  network  solution  to  multi-hop  reasoning.
They build a CNN model based on lexicalized de-
pendency paths, which suffers from the error prop-
agation issue due to parse errors. Guu et al. (2015)
uses KG embeddings to answer path queries. Zeng
et  al.  (2014)  described  a  CNN  model  for  rela-
tional extraction, but it does not explicitly model
the relational paths. Neelakantan et al. (2015) pro-
pose a recurrent neural networks model for model-
ing relational paths in knowledge base completion
(KBC), but it trains too many separate models, and
therefore it does not scale.  Note that many of the
recent KG reasoning methods (Neelakantan et al.,
2015; Das et al., 2017) still rely on first learning
the PRA paths, which only operates in a discrete
space.   Comparing  to  PRA,  our  method  reasons
in a continuous space, and by incorporating vari-
ous criteria in the reward function, our reinforce-
ment learning (RL) framework has better control
and more flexibility over the path-finding process.
Neural  symbolic  machine  (Liang  et  al.,  2016)
is  a  more  recent  work  on  KG  reasoning,  which
also applies reinforcement learning but has a dif-
ferent flavor from our work.  NSM learns to com-
pose programs that can find answers to natural lan-
guage questions, while our RL model tries to add
new facts to knowledge graph (KG) by reasoning
on existing KG triples.   In order to get answers,
NSM learns to generate a sequence of actions that
can be combined as a executable program. The ac-
tion space in NSM is a set of predefined tokens. In
our framework, the goal is to find reasoning paths,
thus the action space is relation space in the KG. A
similar framework (Johnson et al., 2017) has also
been applied to visual reasoning tasks.
## 3    Methodology
In this section, we describe in detail our RL-based
framework for multi-hop relation reasoning.  The
specific  task  of  relation  reasoning  is  to  find  re-
liable  predictive  paths  between  entity  pairs.   We
formulate  the  path  finding problem  as a  sequen-
tial decision making problem which can be solved
with  a  RL  agent.   We  first  describe  the  environ-
ment and the policy-based RL agent.  By interact-
ing with the environment designed around the KG,
the agent learns to pick the promising reasoning
paths. Then we describe the training procedure of
our RL model. After that, we describe an efficient
path-constrained search algorithm for relation rea-
soning with the paths found by the RL agent.
3.1    Reinforcement Learning for Relation
## Reasoning
The  RL  system  consists  of  two  parts  (see  Fig-
ure 1).  The first part is the external environment
Ewhich specifies the dynamics of the interaction
between the agent and the KG. This environment
is modeled as a Markov decision process (MDP).
A tuple<S,A,P,R>is defined to represent
the MDP, whereSis the continuous state space,
## A={a
## 1
## ,a
## 2
## ,...,a
n
}is the set of all available ac-

Band	of
## Brothers
Mini-Series
## HBO
tvProgramCreator
tvProgramGenre
## Graham
## Yost
writtenBy
## Michael
## Kamen
music
## United
## States
countryOfOrigin
## Neal
McDonough
## English
## Tom	Hanks
awardWorkWinner
castActor
## Actor
## ...
profession
personLanguages
## Caesars
## Entertain...
serviceLocation
## -1
The	KG	Environment
## State
## 훑(a|s)
ReLU
ReLU
## Softmax
## Next	State
## Reward
## Reason	Step
## Policy	Based	Agent
Query	Node:	Band	of	Brothers
Reason	Task:	tvProgramLanguage
Figure 1: Overview of our RL model.Left:The KG environmentEmodeled by a MDP. The dotted arrows (partially) show the
existing relation links in the KG and the bold arrows show the reasoning paths found by the RL agent.
## −1
denotes the inverse
of an relation.Right:The structure of the policy network agent.  At each step, by interacting with the environment, the agent
learns to pick a relation link to extend the reasoning paths.
tions,P(S
t+1
## =s
## ′
## |S
t
=s,A
t
=a)is the transi-
tion probability matrix, andR(s,a)is the reward
function of every(s,a)pairs.
The   second   part   of   the   system,    the   RL
agent,is   represented   as   a   policy   network
π
θ
(s,a) =p(a|s;θ)which  maps  the  state  vec-
tor  to  a  stochastic  policy.    The  neural  network
parametersθare  updated  using  stochastic  gra-
dient  descent.Compared  to  Deep  Q  Network
(DQN)  (Mnih  et  al.,  2013),   policy-based  RL
methods turn out to be more appropriate for our
knowledge  graph  scenario.    One  reason  is  that
for  the  path  finding  problem  in  KG,  the  action
space can be very large due to complexity of the
relation graph.  This can lead to poor convergence
properties for DQN. Besides,  instead of learning
a greedy policy which is common in value-based
methods like DQN, the policy network is able to
learn a stochastic policy which prevent the agent
from getting stuck at an intermediate state. Before
we describe  the structure  of our policy  network,
we first describe the components (actions, states,
rewards) of the RL environment.
ActionsGiven   the   entity   pairs(e
s
## ,e
t
## )with
relationr,  we  want  the  agent  to  find  the  most
informative   paths   linking   these   entity   pairs.
Beginning with the source entitye
s
, the agent use
the  policy  network  to  pick  the  most  promising
relation  to  extend  its  path  at  each  step  until  it
reaches  the  target  entitye
t
.   To  keep  the  output
dimension  of  the  policy  network  consistent,  the
action space is defined as all the relations in the
## KG.
StatesThe  entities  and  relations  in  a  KG  are
naturally  discrete  atomic  symbols.   Since  exist-
ing practical KGs like Freebase (Bollacker et al.,
2008) and NELL (Carlson et al., 2010b) often have
huge  amounts  of  triples.   It  is  impossible  to  di-
rectly model all the symbolic atoms in states.  To
capture  the  semantic  information  of  these  sym-
bols, we use translation-based embeddings such as
TransE  (Bordes  et  al.,  2013)  and  TransH  (Wang
et al., 2014) to represent the entities and relations.
These embeddings map all the symbols to a low-
dimensional vector space. In our framework, each
state captures the agent’s position in the KG. After
taking an action, the agent will move from one en-
tity to another. These two are linked by the action
(relation) just taken by the agent. The state vector
at steptis given as follows:
s
t
## = (e
t
## ,e
target
## −e
t
## )
wheree
t
denotes  the  embeddings  of  the  current

entity node ande
target
denotes the embeddings of
the target entity.  At the initial state,e
t
## =e
source
## .
We  do  not  incorporate  the  reasoning  relation  in
the state, because the embedding of the reasoning
relation   remain   constant   during   path   finding,
which  is  not  helpful  in  training.    However,  we
find out that by training the RL agent using a set
of  positive  samples  for  one  particular  relation,
the  agent  can  successfully  discover  the  relation
semantics.
RewardsThere are a few factors that contribute to
the quality of the paths found by the RL agent. To
encourage the agent to find predictive paths,  our
reward functions include the following scoring cri-
teria:
Global  accuracy:For  our  environment  settings,
the  number  of  actions  that  can  be  taken  by  the
agent can be very large.  In other words, there are
much more incorrect sequential decisions than the
correct ones.   The number of these incorrect de-
cision sequences can increase exponentially with
the length of the path.  In view of this challenge,
the first reward function we add to the RL model
is defined as follows:
r
## GLOBAL
## =
## {
+1,if the path reachese
target
## −1,otherwise
the agent is given an offline positive reward+1if
it reaches the target after a sequence of actions.
Path  efficiency:For  the  relation  reasoning  task,
we observe that short paths tend to provide more
reliable  reasoning  evidence  than  longer  paths.
Shorter  chains  of  relations  can  also  improve  the
efficiency of the reasoning by limiting the length
of the RL’s interactions with the environment. The
efficiency reward is defined as follows:
r
## EFFICIENCY
## =
## 1
length(p)
where pathpis defined as a sequence of relations
r
## 1
## →r
## 2
## →...→r
n
## .
Path diversity:We train the agent to find paths us-
ing positive samples for each relation. These train-
ing sample(e
source
## ,e
target
)have similar state rep-
resentations in the vector space.  The agent tends
to  find  paths  with  similar  syntax  and  semantics.
These paths often contains redundant information
since some of them may be correlated. To encour-
age the agent to find diverse paths, we define a di-
versity reward function using the cosine similarity
between the current path and the existing ones:
r
## DIVERSITY
## =−
## 1
## |F|
## |F|
## ∑
i=1
cos(p,p
i
## )
wherep=
## ∑
n
i=1
r
i
represents the path embed-
ding for the relation chainr
## 1
## →r
## 2
## →...→r
n
## .
Policy  NetworkWe  use  a  fully-connected  neu-
ral  network  to  parameterize  the  policy  function
π(s;θ)that  maps  the  state  vectorsto  a  proba-
bility  distribution  over  all  possible  actions.   The
neural network consists of two hidden layers, each
followed by a rectifier nonlinearity layer (ReLU).
The  output  layer  is  normalized  using  a  softmax
function (see Figure 1).
## 3.2    Training Pipeline
In practice, one big challenge of KG reasoning is
that the relation set can be quite large.  For a typ-
ical  KG,  the  RL  agent  is  often  faced  with  hun-
dreds  (thousands)  of  possible  actions.    In  other
words, the output layer of the policy network of-
ten has a large dimension.  Due to the complexity
of  the  relation  graph  and  the  large  action  space,
if we directly train the RL model by trial and er-
rors,  which is typical for RL algorithms,  the RL
model  will  show  very  poor  convergence  proper-
ties.   After  a  long-time  training,  the  agents  fails
to  find  any  valuable  path.   To  tackle  this  prob-
lem, we start our training with a supervised policy
which is inspired by the imitation learning pipeline
used byAlphaGo(Silver et al., 2016).  In the Go
game, the player is facing nearly 250 possible le-
gal moves at each step. Directly training the agent
to pick actions from the original action space can
be a difficult task.AlphaGofirst train a supervised
policy network using experts moves.  In our case,
the supervised policy is trained with a randomized
breadth-first search (BFS).
Supervised  Policy  LearningFor  each  relation,
we  use  a  subset  of  all  the  positive  samples  (en-
tity pairs) to learn the supervised policy. For each
positive sample(e
source
## ,e
target
), a two-side BFS
is  conducted to  find  same  correct  paths  between
the entities.   For each pathpwith a sequence of
relationsr
## 1
## →r
## 2
## →...→r
n
, we update the pa-
rametersθto maximize the expected cumulative
reward  using  Monte-Carlo  Policy  Gradient  (RE-

INFORCE) (Williams, 1992):
J(θ) =E
a∼π(a|s;θ)
## (
## ∑
t
## R
s
t
## ,a
t
## )
## =
## ∑
t
## ∑
a∈A
π(a|s
t
;θ)R
s
t
## ,a
t
## (1)
whereJ(θ)is the expected total rewards for one
episode.   For  supervised  learning,  we  give  a  re-
ward of+1for each step of a successful episode.
By plugging in  the paths found by the  BFS, the
approximated  gradient used  to  update the  policy
network is shown below:
## ∇
θ
## J(θ) =
## ∑
t
## ∑
a∈A
π(a|s
t
## ;θ)∇
θ
logπ(a|s
t
## ;θ)
## ≈∇
θ
## ∑
t
logπ(a=r
t
## |s
t
## ;θ)(2)
wherer
t
belongs to the pathp.
However, the vanilla BFS is a biased search al-
gorithm  which  prefers  short  paths.   When  plug-
ging  in  these  biased  paths,  it  becomes  difficult
for the agent to find longer paths which may po-
tentially  be  useful.We  want  the  paths  to  be
controlled  only  by  the  defined  reward  functions.
To  prevent  the  biased  search,  we  adopt  a  sim-
ple trick to add some random mechanisms to the
BFS.  Instead  of  directly  searching  the  path  be-
tweene
source
ande
target
, we randomly pick a in-
termediate nodee
inter
and then conduct two BFS
between(e
source
## ,e
inter
## )and(e
inter
## ,e
target
## ). The
concatenated paths are used to train the agent. The
supervised  learning  saves  the  agent  great  efforts
learning from failed actions.  With the learned ex-
perience, we then train the agent to find desirable
paths.
Retraining with RewardsTo find the reasoning
paths controlled by the reward functions, we use
reward functions to retrain the supervised policy
network. For each relation, the reasoning with one
entity pair is treated as one episode. Starting with
the source nodee
source
, the agent picks a relation
according to the stochastic policyπ(a|s), which is
a probability distribution over all relations, to ex-
tend its reasoning path. This relation link may lead
to a new entity, or it may lead to nothing.  These
failed steps will cause the agent to receive negative
rewards.  The agent will stay at the same state af-
ter these failed steps. Since the agent is following
a stochastic policy, the agent will not get stuck by
repeating a wrong step. To improve the training ef-
ficiency, we limit the episode length with an upper
Algorithm  1:Retraining  Procedure  with  re-
ward functions
1Restore parametersθfrom supervised policy;
2forepisode←1toNdo
3Initialize state vectors
t
## ←s
## 0
4Initialize episode lengthsteps←0
## 5whilenum
steps < maxlengthdo
6Randomly sample actiona∼π(a|s
t
## )
7Observe rewardR
t
, next states
t+1
// if the step fails
8ifR
t
## =−1then
9Save< s
t
,a >toM
neg
10ifsuccess orsteps=maxlength
then
## 11break
12Incrementnumsteps
// penalize failed steps
13Updateθusing
g∝∇
θ
## ∑
## M
neg
logπ(a=r
t
## |s
t
## ;θ)(−1)
ifsuccessthen
## 14R
total
## ←λ
## 1
r
## GLOBAL
## +λ
## 2
r
## EFFICIENCY
## +
λ
## 3
r
## DIVERSITY
15Updateθusing
g∝∇
θ
## ∑
t
logπ(a=r
t
## |s
t
;θ)R
total
boundmaxlength. The episode ends if the agent
fails to reach the target entity withinmaxlength
steps.   After each episode,  the policy network is
updated using the following gradient:
## ∇
θ
## J(θ) =∇
θ
## ∑
t
logπ(a=r
t
## |s
t
;θ)R
total
## (3)
whereR
total
is the linear combination of the de-
fined reward functions.   The detail of the retrain
process is shown in Algorithm 1.  In practice,θis
updated using the Adam Optimizer (Kingma and
Ba, 2014) with L
## 2
regularization.
## 3.3    Bi-directional Path-constrained Search
Given an entity pair, the reasoning paths learned
by the RL agent can be used as logical formulas
to predict the relation link.  Each formula is veri-
fied using a bi-directional search. In a typical KG,
one entity node can be linked to a large number
of neighbors with the same relation link.  A sim-
ple  example  is  the  relationpersonNationality
## −1
## ,
which  denotes  the  inverse  ofpersonNationality.
Following  this  link,  the  entityUnited  Statescan
reach  numerous  neighboring  entities.   If  the  for-

Algorithm  2:Bi-directional  search  for  path
verification
1Given a reasoning path
p:r
## 1
## →r
## 2
## →...→r
n
## 2for(e
i
## ,e
j
)in test setDdo
3start←0; end←n
## 4left←∅;right←∅
## 5whilestart<enddo
6leftEx←∅;rightEx←∅
## 7iflen(left)<len(right)then
8Extend path on the left side
9Add connected nodes toleftEx
10left←leftEx
## 11else
12Extend path on the right side
13Add connected nodes torightEx
14right←rightEx
## 15ifleft∩right6=∅then
16returnTrue
## 17else
18returnFalse
mula consists of such links, the number of inter-
mediate entities can exponentially increase as we
follow the  reasoning formula.   However,  we  ob-
serve that for these formulas, if we verify the for-
mula from the inverse direction. The number of in-
termediate nodes can be tremendously decreased.
Algorithm  2  shows  a  detailed  description  of  the
proposed bi-directional search.
## 4    Experiments
To evaluate the reasoning formulas found by our
RL  agent,  we  explore  two  standard  KG  reason-
ing  tasks:   link  prediction  (predicting  target  en-
tities) and fact prediction (predicting whether an
unknown  fact  holds  or  not).    We  compare  our
method with both path-based methods and embed-
ding based methods. After that, we further analyze
the reasoning paths found by our RL agent. These
highly predictive paths validate the effectiveness
of the reward functions. Finally, we conduct a ex-
periment to investigate the effect of the supervised
learning procedure.
4.1    Dataset and Settings
Table  1  shows  the  statistics  of  the  two  datasets
we  conduct  our  experiments  on.   Both  of  them
## Dataset# Ent.# R.# Triples# Tasks
## FB15K-23714,505237310,11620
## NELL-99575,492200154.21312
Table 1: Statistics of the Datasets. # Ent. denotes the number
of unique entities and # R. denotes the number of relations
are  subsets  of  larger  datasets.The  triples  in
FB15K-237 (Toutanova et al., 2015) are sampled
from  FB15K  (Bordes  et  al.,  2013)  with  redun-
dant relations removed. We perform the reasoning
tasks on 20 relations which have enough reason-
ing paths.  These tasks consists of relations from
different domains likeSports,People,Locations,
Film, etc.  Besides, we present a new NELL sub-
set  that  is  suitable  for  multi-hop  reasoning  from
the 995th iteration of the NELL system.  We first
remove the triples with relationgeneralizationsor
haswikipediaurl. These two relations appear more
than 2M times in the NELL dataset, but they have
no reasoning values.  After this step, we only se-
lect the triples with Top-200 relations. To facilitate
path finding, we also add the inverse triples.  For
each triple(h,r,t),  we append(t,r
## −1
,h)to the
datasets.   With these inverse triples,  the agent is
able to step backward in the KG.
For each reasoning taskr
i
,  we remove all the
triples withr
i
orr
## −1
i
from the KG. These removed
triples  are  split  into  train  and  test  samples.   For
the link prediction task, eachhin the test triples
{(h,r,t)}is  considered  as  one  query.   A  set  of
candidate target entities are ranked using different
methods.  For fact prediction, the true test triples
are ranked with some generated false triples.
4.2    Baselines and Implementation Details
Most KG reasoning methods are based on either
path  formulas  or  KG  embeddings.    we  explore
methods from both of these two classes in our ex-
periments.  For path based methods, we compare
our RL model with the PRA (Lao et al., 2011a)
algorithm, which has been used in a couple of rea-
soning methods (Gardner et al., 2013; Neelakan-
tan et al., 2015).  PRA is a data-driven algorithm
using random walks (RW) to find paths and obtain
path features.  For embedding based methods, we
evaluate  several  state-of-the-art  embeddings  de-
signed  for  knowledge  base  completion,  such  as
TransE (Bordes et al., 2013), TransH (Wang et al.,
2014),  TransR  (Lin  et  al.,  2015)  and  TransD  (Ji
et al., 2015) .
The  implementation  of  PRA  is  based  on  the

## FB15K-237NELL-995
TasksPRARLTransETransRTasksPRARLTransETransR
teamSports0.9870.9550.8960.784athletePlaysForTeam0.5470.7500.6270.673
birthPlace0.4410.5310.4030.417athletePlaysInLeague0.8410.9600.7730.912
personNationality0.8460.8230.6410.720athleteHomeStadium0.8590.8900.7180.722
filmDirector0.3490.4410.3860.399athletePlaysSport0.4740.9570.8760.963
filmWrittenBy0.6010.4570.5630.605teamPlaySports0.7910.7380.7610.814
filmLanguage0.6630.6700.6420.641orgHeadquaterCity0.8110.7900.6200.657
tvLanguage0.9600.9690.8040.906worksFor0.6810.7110.6770.692
capitalOf0.8290.7830.5540.493bornLocation0.6680.7570.7120.812
organizationFounded0.2810.3090.3900.339personLeadsOrg0.7000.7950.7510.772
musicianOrigin0.4260.5140.3610.379orgHiredPerson0.5990.7420.7190.737
## ......
## Overall0.5410.5720.5320.5400.6750.7960.7370.789
Table 2: Link prediction results (MAP) on two datasets.
code released by (Lao et al., 2011a).  We use the
TopK negative mode to generate negative samples
for  both  train  and  test  samples.    For  each  pos-
itive  samples,  there  are  approximately  10  corre-
sponding negative samples. Each negative sample
is  generated  by  replacing  the  true  target  entityt
with a faked onet
## ′
in each triple(h,r,t).  These
positive and negative test pairs generated by PRA
make up the test set for all methods evaluated in
this paper. For TransE,R,H,D, we learn a separate
embedding  matrix  for  each  reasoning  task  using
the positive training entity pairs. All these embed-
dings are trained for 1,000 epochs.
## 2
Our RL model make use of TransE to get the
continuous representation of the entities and rela-
tions.   We use the same dimension as TransE, R
to embed the entities.  Specifically, the state vec-
tor we use has a dimension of 200, which is also
the  input  size  of  the  policy  network.   To  reason
using  the  path  formulas,  we  adopt  a  similar  lin-
ear regression approach as in PRA to re-rank the
paths. However, instead of using the random walk
probabilities as path features, which can be com-
putationally expensive, we simply use binary path
features obtained by the bi-directional search. We
observe that with only a few mined path formulas,
our method can achieve better results than PRA’s
data-driven approach.
## 4.3    Results
## 4.3.1    Quantitative Results
Link PredictionThis task is to rank the target en-
tities given a query entity. Table 2 shows the mean
average precision (MAP) results on two datasets.
## 2
The implementation we used can be found athttps:
//github.com/thunlp/Fast-TransX
## Fact Prediction Results
MethodsFB15K-237NELL-995
## RL0.3110.493
TransE0.2770.383
TransH0.309
## 0.389
TransR0.3020.406
TransD0.3030.413
Table 3: Fact prediction results (MAP) on two datasets.
# of Reasoning Paths
TasksPRARL
worksFor24725
teamPlaySports11327
teamPlaysInLeague6921
athletehomestadium3711
organizationHiredPerson2449
## ...
## Average #137.220.3
Table 4: Number of reasoning paths used by PRA and our RL
model.RL achieved better MAP with a more compact set of
learned paths.
Since  path-based  methods  generally  work  better
than embedding methods for this task, we do not
include the other two embedding baselines in this
table.  Instead, we spare the room to show the de-
tailed results on each relation reasoning task.
For the overall MAP shown in the last row of the
table, our approach significantly outperforms both
the path-based method and embedding methods on
two datasets, which validates the strong reasoning
ability of our RL model. For most relations, since
the embedding methods fail to use the path infor-

## 0510152025
distribution of reasoning paths
## 0
## 20
## 40
## 60
## 80
## 100
## 120
number of paths
## NELL-995
## FB15K-237
Figure 2: The distribution of paths lengths on two datasets
mation in the KG, they generally perform worse
than our RL model or PRA. However, when there
are not enough paths between entities, our model
and  PRA  can  give  poor  results.    For  example,
for the relationfilmWrittenBy, our RL model only
finds 4 unique reasoning paths, which means there
is actually not enough reasoning evidence existing
in the KG. Another observation is that we always
get better performance on the NELL dataset.  By
analyzing the paths found from the KGs, we be-
lieve the potential reason is that the NELL dataset
has more short paths than FB15K-237 and some
of them are simply synonyms of the reasoning re-
lations.
Fact PredictionInstead of ranking the target en-
tities, this task directly ranks all the positive and
negative  samples  for  a  particular  relation.    The
PRA is not included as a baseline here, since the
PRA  code  only  gives  a  target  entity  ranking  for
each query node instead of a ranking of all triples.
Table 3 shows the overall results of all the meth-
ods. Our RL model gets even better results on this
task.  We also observe that the RL model beats all
the embedding baselines on most reasoning tasks.
4.3.2    Qualitative Analysis of Reasoning Paths
To analyze the properties of reasoning paths, we
show  a  few  reasoning  paths  found  by  the  agent
in  Table  5.    To  illustrate  the  effect  of  the  effi-
ciency reward function, we show the path length
distributions in Figure 2.  To interpret these paths,
take  thepersonNationalityrelation  for  example,
the first reasoning path indicates that if we know
factsplaceOfBirth(x,y)andlocationContains(z,y)
then it is highly possible that personxhas nation-
alityz.  These short but predictive paths indicate
the effectiveness of the RL model.   Another im-
portant  observation  is  that  our  model  use  much
## 050100150200
training episodes
## 0.00
## 0.05
## 0.10
## 0.15
## 0.20
success ratio within 10 steps
Figure 3:  The success ratio (succ
## 10
) during training.  Task:
athletePlaysForTeam.
## 3
fewer reasoning paths than PRA, which indicates
that our model can actually extract the most reli-
able reasoning evidence from KG. Table 4 shows
some comparisons about the number of reasoning
paths.   We can see that,  with the pre-defined re-
ward functions, the RL agent is capable of picking
the strong ones and filter out similar or irrelevant
ones.
4.3.3    Effect of Supervised Learning
As mentioned in Section 3.2, one major challenge
for applying RL to KG reasoning is the large ac-
tion  space.    We  address  this  issue  by  applying
supervised  learning  before  the  reward  retraining
step.  To show the effect of the supervised train-
ing, we evaluate the agent’s success ratio of reach-
ing the target within 10 steps (succ
## 10
) after differ-
ent number of training episodes.  For each train-
ing episode, one pair of entities(e
source
## ,e
target
## )
in the train set is used to find paths.  All the cor-
rect paths linking the entities will get a+1global
reward. We then plug in some true paths for train-
ing. Thesucc
## 10
is calculated on a held-out test set
that consists of 100 entity pairs.  For the NELL-
995 dataset,  since we have 200 unique relations,
the dimension of the action space will be 400 af-
ter we add the backward actions.  This means that
random walks will get very lowsucc
## 10
since there
may be nearly400
## 10
invalid paths. Figure 3 shows
thesucc
## 10
during training.  We see that even the
agent has not seen the entity before, it can actually
pick the promising relation to extend its path. This
also validates the effectiveness of our state repre-
sentations.
## 3
The confidence band is generated using 50 different runs.

RelationReasoning Path
filmCountry
filmReleaseRegion
featureFilmLocation→locationContains
## −1
actorFilm
## −1
→personNationality
personNationality
placeOfBirth→locationContains
## −1
peoplePlaceLived→locationContains
## −1
peopleMarriage→locationOfCeremony→locationContains
## −1
tvProgramLanguage
tvCountryOfOrigin→countryOfficialLanguage
tvCountryOfOrigin→filmReleaseRegion
## −1
→filmLanguage
tvCastActor→filmLanguage
personBornInLocation
personBornInCity
graduatedUniversity→graduatedSchool
## −1
→personBornInCity
personBornInCity→atLocation
## −1
→atLocation
athletePlaysForTeam
athleteHomeStadium→teamHomeStadium
## −1
athletePlaysSport→teamPlaysSport
## −1
athleteLedSportsTeam
personLeadsOrganization
worksFor
organizationTerminatedPerson
## −1
mutualProxyFor
## −1
Table 5:  Example reasoning paths found by our RL model.  The first three relations come from the FB15K-237 dataset.  The
others are from NELL-995. Inverses of existing relations are denoted by
## −1
## .
5    Conclusion and Future Work
In this paper,  we propose a reinforcement learn-
ing framework to improve the performance of re-
lation reasoning in KGs.  Specifically, we train a
RL agent to find reasoning paths in the knowledge
base. Unlike previous path finding models that are
based on random walks, the RL model allows us
to control the properties of the found paths. These
effective paths can also be used as an alternative to
PRA in many path-based reasoning methods.  For
two standard reasoning tasks, using the RL paths
as reasoning formulas, our approach generally out-
performs two classes of baselines.
For   future   studies,   we   plan   to   investigate
the possibility of incorporating adversarial learn-
ing  (Goodfellow  et  al.,  2014)  to  give  better  re-
wards  than  the  human-defined  reward  functions
used in this work.   Instead of designing rewards
according to path characteristics, a discriminative
model can be trained to give rewards. Also, to ad-
dress the problematic scenario when the KG does
not have enough reasoning paths, we are interested
in applying our RL framework to joint reasoning
with KG triples and text mentions.
## Acknowledgments
We    gratefully    acknowledge    the    support    of
NVIDIA Corporation with the donation of one Ti-
tan X Pascal GPU used for this research.
## References
## Kurt  Bollacker,  Colin  Evans,  Praveen  Paritosh,  Tim
Sturge, and Jamie Taylor. 2008.  Freebase: a collab-
oratively created graph database for structuring hu-
man knowledge.  InProceedings of the 2008 ACM
SIGMOD international conference on Management
of data, pages 1247–1250. ACM.
## Antoine  Bordes,   Nicolas  Usunier,   Alberto  Garcia-
Duran,   Jason   Weston,   and   Oksana   Yakhnenko.
-  Translating embeddings for modeling multi-
relational data.   InAdvances in neural information
processing systems, pages 2787–2795.
## Andrew Carlson, Justin Betteridge, Bryan Kisiel, Burr
Settles,   Estevam  R.  Hruschka  Jr.,   and  Tom  M.
Mitchell. 2010a.  Toward an architecture for never-
ending language learning. InAAAI.
## Andrew Carlson, Justin Betteridge, Bryan Kisiel, Burr
Settles,   Estevam  R.  Hruschka  Jr.,   and  Tom  M.
Mitchell. 2010b.  Toward an architecture for never-
ending  language  learning.    InProceedings  of  the
Twenty-Fourth Conference on Artificial Intelligence
## (AAAI 2010).

## Rajarshi  Das,  Arvind  Neelakantan,  David  Belanger,
and Andrew McCallum. 2017.  Chains of reasoning
over entities, relations, and text using recurrent neu-
ral networks.EACL.
## Matt  Gardner,  Partha  Pratim  Talukdar,  Bryan  Kisiel,
and  Tom  M  Mitchell.  2013.Improving  learning
and inference in a large knowledge-base using latent
syntactic cues. InEMNLP, pages 833–838.
## Matt Gardner, Partha Pratim Talukdar, Jayant Krishna-
murthy, and Tom Mitchell. 2014. Incorporating vec-
tor space similarity in random walk inference over
knowledge bases.
Ian  Goodfellow,  Jean  Pouget-Abadie,  Mehdi  Mirza,
Bing Xu, David Warde-Farley, Sherjil Ozair, Aaron
Courville, and Yoshua Bengio. 2014. Generative ad-
versarial nets.   InAdvances in Neural Information
Processing Systems, pages 2672–2680.
Kelvin  Guu,   John  Miller,   and  Percy  Liang.  2015.
Traversing  knowledge  graphs  in  vector  space.    In
## EMNLP.
## Geoffrey Hinton, Li Deng, Dong Yu, George E Dahl,
## Abdel-rahman  Mohamed,  Navdeep  Jaitly,  Andrew
## Senior, Vincent Vanhoucke, Patrick Nguyen, Tara N
Sainath,  et  al.  2012.Deep  neural  networks  for
acoustic modeling in speech recognition: The shared
views of four research groups.IEEE Signal Process-
ing Magazine, 29(6):82–97.
Guoliang Ji, Shizhu He, Liheng Xu, Kang Liu, and Jun
Zhao. 2015.   Knowledge graph embedding via dy-
namic mapping matrix. InACL (1), pages 687–696.
Justin  Johnson,  Bharath  Hariharan,  Laurens  van  der
Maaten, Judy Hoffman, Li Fei-Fei, C Lawrence Zit-
nick,  and Ross Girshick. 2017.   Inferring and exe-
cuting programs for visual reasoning.arXiv preprint
arXiv:1705.03633.
Yoon   Kim.   2014.Convolutional   neural   net-
works  for  sentence  classification.arXiv  preprint
arXiv:1408.5882.
Diederik  Kingma  and  Jimmy  Ba.  2014.Adam:   A
method for stochastic optimization.arXiv preprint
arXiv:1412.6980.
Alex Krizhevsky, Ilya Sutskever, and Geoffrey E Hin-
ton.  2012.   Imagenet  classification  with  deep  con-
volutional neural networks.   InAdvances in neural
information processing systems, pages 1097–1105.
Ni Lao, Tom Mitchell, and William W Cohen. 2011a.
Random walk inference and learning in a large scale
knowledge base.  InProceedings of the Conference
on  Empirical  Methods  in  Natural  Language  Pro-
cessing, pages 529–539. Association for Computa-
tional Linguistics.
Ni  Lao,  Tom  M.  Mitchell,  and  William  W.  Cohen.
2011b.   Random  walk  inference  and  learning  in  a
large scale knowledge base. InEMNLP, pages 529–
## 539. ACL.
Ni  Lao,  Jun  Zhu,  Xinwang  Liu,  Yandong  Liu,  and
William W Cohen. 2010.  Efficient relational learn-
ing with hidden variable detection.  InNIPS, pages
## 1234–1242.
## Chen  Liang,  Jonathan  Berant,  Quoc  Le,  Kenneth  D
Forbus,   and   Ni   Lao.   2016.Neural   symbolic
machines:Learning   semantic   parsers   on   free-
base   with   weak   supervision.arXiv   preprint
arXiv:1611.00020.
Yankai Lin, Zhiyuan Liu, Maosong Sun, Yang Liu, and
Xuan Zhu. 2015.  Learning entity and relation em-
beddings for knowledge graph completion. InAAAI,
pages 2181–2187.
## Volodymyr  Mnih,   Koray  Kavukcuoglu,   David  Sil-
ver, Alex Graves, Ioannis Antonoglou, Daan Wier-
stra,  and  Martin  Riedmiller.  2013.Playing  atari
with  deep  reinforcement  learning.arXiv  preprint
arXiv:1312.5602.
## Volodymyr Mnih,  Koray Kavukcuoglu,  David Silver,
## Andrei  A  Rusu,  Joel  Veness,  Marc  G  Bellemare,
## Alex Graves,  Martin Riedmiller,  Andreas K Fidje-
land,  Georg  Ostrovski,  et  al.  2015.    Human-level
control  through  deep  reinforcement  learning.Na-
ture, 518(7540):529–533.
Arvind Neelakantan, Benjamin Roth, and Andrew Mc-
Callum.  2015.    Compositional  vector  space  mod-
els for knowledge base completion.arXiv preprint
arXiv:1504.06662.
## David  Silver,  Aja  Huang,  Chris  J  Maddison,  Arthur
## Guez, Laurent Sifre, George Van Den Driessche, Ju-
lian  Schrittwieser,  Ioannis  Antonoglou,  Veda  Pan-
neershelvam, Marc Lanctot, et al. 2016.  Mastering
the game of go with deep neural networks and tree
search.Nature, 529(7587):484–489.
## Kristina Toutanova, Danqi Chen, Patrick Pantel, Hoi-
fung Poon, Pallavi Choudhury, and Michael Gamon.
-  Representing text for joint embedding of text
and knowledge bases. InEMNLP, volume 15, pages
## 1499–1509. Citeseer.
William  Yang  Wang  and  William  W  Cohen.  2015.
Joint information extraction and reasoning:  A scal-
able statistical relational learning approach. InACL.
Zhen Wang, Jianwen Zhang, Jianlin Feng, and Zheng
Chen. 2014. Knowledge graph embedding by trans-
lating on hyperplanes.  InAAAI, pages 1112–1119.
## Citeseer.
Ronald J Williams. 1992.  Simple statistical gradient-
following  algorithms  for  connectionist  reinforce-
ment learning.Machine learning, 8(3-4):229–256.
## Daojian Zeng, Kang Liu, Siwei Lai, Guangyou Zhou,
Jun  Zhao,  et  al.  2014.   Relation  classification  via
convolutional  deep  neural  network.    InCOLING,
pages 2335–2344.