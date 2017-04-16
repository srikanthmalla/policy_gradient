#main file
#Policy Gradient: using REINFORCE Algorithm
import gym
#import matplotlib.pyplot as plt #for visualization
import critic
import actor
import random

import numpy as np
NUM_EPOCHS = 1000
GAMMA = 0.99

no_of_actions=2 #find depeding on which environment it is

# reproducible
np.random.seed(1)

if __name__=="__main__":
	epsilon =0.9
	#initialize gym environment
	env = gym.make("CartPole-v0")
	observation = env.reset()
	print observation.shape

	#Initialize Actor
	actor = actor.Actor(4,2)
	actor.createModel()	
	#Initialize Critic
	critic = critic.Critic(4)
	critic.createModel()	
	#for n policies 		
	for i in range(NUM_EPOCHS):
		#epsilon=epsilon-0.4*(float(i)/NUM_EPOCHS)
		epsilon=epsilon-0.001
		#for each rollout <s,a,r>
		observation_old = env.reset()
		T=[]
		tot_reward = 0
		for _ in range(400):
			env.render()
			observation_old = np.reshape(observation_old,(1,4))
			action_prob = actor.act(observation_old)
			#toss=np.random.rand(1,1)
			toss = random.random()
			if (epsilon < toss):			
				action = np.argmax(action_prob)
			else:	
				action = np.random.randint(2, size=1) #rand integer
				action = action.item(0)		
			observation_new, reward, done, info = env.step(action)
			observation_new = np.reshape(observation_new,(1,4))
			T.append([observation_old,action,reward])
			tot_reward = tot_reward + reward
		        observation_old=observation_new
			if done:
				break
		print "Episode:",i,"epsilon:",epsilon,"Total Reward : ",tot_reward		
		#print T

		# Get Rt then T will become <s,a,r,R>
		#T[len(T)-1].append(T[len(T)-1][2])		
		for i in range(len(T)-1):
			#T[i].append(T[i][2]+GAMMA*T[i+1][3])
			T[i].append(T[i][2] + GAMMA*critic.Value(T[i+1][0]))
		T[len(T)-1].append(T[len(T)-1][2]) 

		# find bt which is a value from critic, then T becomes <s,a,r,R,b>
		for i in range(len(T)):
			T[i].append(critic.Value(T[i][0]))

		#find A which is Advantage (R-b), then T becomes <s,a,r,R,b,A>
		for i in range(len(T)):
			T[i].append(T[i][-2]-T[i][-1])

		#train critic using states and R (actual values from environment)
		states=T[0][0]	
		for i in range(1,len(T)):		
			states=np.vstack((states,T[i][0]))
		values=T[0][3]
		for i in range(1,len(T)):
			values=np.vstack((values,np.array(T[i][3])))		
		#print "states shape:",np.shape(states)
		#print "values shape:",np.shape(values)
		critic.train(states,values)

		#train actor using states actions and advantage (for computing gradients too)
		advantages=T[0][5]	
		for i in range(1,len(T)):		
			advantages=np.vstack((advantages,T[i][5]))
		z=np.zeros((np.shape((1,no_of_actions))))		
		t=z
		t[[T[0][1]]]=1		
		actions=t
		for i in range(1,len(T)): 
			t=z
			t[[T[0][1]]]=1
			actions=np.vstack((actions,t))
		#print np.shape(states),np.shape(actions),np.shape(advantages)
		actor.train(states,actions,advantages)

		
