# Name: Kaustubh Sharma
# College: BITS Pilani
# Roll Number: REPLACE_WITH_ROLL

import random

POWER_VALUES={"FORESIGHT":{1:0.76,2:1.16,3:1.48,4:1.97,5:2.02},"TRICK_ROOM":{1:1.14,2:0.0,3:0.0,4:0.60,5:0.52},"SUBSTITUTE":{1:1.46,2:1.15,3:0.95,4:0.57,5:0.29},"STEALTH_ROCK":{1:1.51,2:1.0,3:0.8,4:0.75,5:0.0},"TRANSFORM":{1:1.58,2:1.24,3:1.31,4:0.0,5:0.0}}

class Bot:
    name='QuantStormAlpha'
    def reset(self,seat,config,seed):
        self.seat=seat; self.config=config; self.rng=random.Random(seed); self.opp_mid=[]
    def est(self,obs,quote=None):
        v=float(obs.k_mine)+sum(obs.foresight)
        if quote is not None: v=0.7*v+0.3*((quote[0]+quote[1])/2)
        return v
    def bid(self,obs,offered):
        if not offered or obs.te_mine<=0:return {}
        p=offered[0]; val=POWER_VALUES.get(p,{}).get(obs.round,0.5)
        if p=='FORESIGHT' and obs.round>=4: val*=1.35
        if p=='STEALTH_ROCK' and obs.round<=2: val*=1.25
        if p=='TRANSFORM':
            if abs(obs.k_mine)<=1: val*=1.5
            else: val*=0.3
        future=max(1,6-obs.round)
        shade=0.55 if obs.te_mine<future*3 else 0.68
        bid=min(obs.te_mine,int((val/self.config.TE_SALVAGE)*shade))
        return {p:bid} if bid>0 else {}
    def quote(self,obs):
        v=round(self.est(obs))
        w=obs.final_cap
        return (v-w//2,v-w//2+w)
    def respond(self,obs,quote,turn):
        bid,ask=quote; v=self.est(obs,quote)
        if v-ask>1: return 'ACCEPT_BUY'
        if bid-v>1: return 'ACCEPT_SELL'
        if turn==self.config.N_TURNS:
            return ('COUNTER',bid,ask)
        width=max(obs.final_cap,(ask-bid)-1)
        c=round(v)
        lo=max(bid,min(c-width//2,ask-width))
        return ('COUNTER',lo,lo+width)
    def use_transform(self,obs):
        return abs(obs.k_mine)<=1