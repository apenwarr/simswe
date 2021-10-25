library(ggplot2)
library(reshape2)

r = read.csv('out.csv', header=T, sep=',')
r$strategy = factor(r$strategy, levels=c(
	'features first', 'alternating',
	'blockers first', 'perfectionism')
)

mr = melt(r,
	measure.vars=.(interested, satisfiable, users),
	variable.name='metric',
)
mr$metric = factor(mr$metric,
	c('users', 'interested', 'satisfiable'),
	labels=c('active users', 'market size', 'attainable users'),
)

rr = subset(r, t<350)
rzb = r
rzb$users[rzb$users == 0] = NA

p0 = (
  ggplot(data=subset(r, strategy=='alternating'), aes(x=t, y=users))
  + geom_step(aes(y=interested), linetype=3, size=0.75, color='#444444')
  + geom_step(aes(y=satisfiable), linetype=5, color='#888888')
  + geom_step(color='red', size=0.75)
#  + geom_step(data=subset(r, strategy=='blockers first'), color='purple', size=0.75)
#  + facet_grid(strategy~.)
#  + facet_wrap(~strategy, ncol=1)
  + theme_minimal()
  + theme(#panel.border=element_rect(color='#cccccc'),
          #axis.text.y=element_blank(), axis.ticks.y=element_blank(),
          #strip.text.x = element_blank(),
          #strip.text.y = element_text(size=rel(1.2)),
          #axis.text.x = element_text(angle=90, hjust=1, vjust=0.5)
    )
  + labs(x='Time', y='Users',
  	title='Simulated users over time',
  	subtitle='dotted=addressable market    dashed=unblocked users    red=active users'
    )
)

p = (
  ggplot(data=r, aes(x=t, y=users))
  + geom_step(aes(y=interested), linetype=3, size=0.75, color='#444444')
  + geom_step(aes(y=satisfiable), linetype=5, color='#888888')
  + geom_step(color='red', size=0.75)
#  + geom_step(data=subset(r, strategy=='blockers first'), color='purple', size=0.75)
#  + facet_grid(strategy~.)
  + facet_wrap(~strategy, ncol=1)
  + theme_minimal()
  + theme(#panel.border=element_rect(color='#cccccc'),
          #axis.text.y=element_blank(), axis.ticks.y=element_blank(),
          #strip.text.x = element_blank(),
          #strip.text.y = element_text(size=rel(1.2)),
          #axis.text.x = element_text(angle=90, hjust=1, vjust=0.5)
    )
  + labs(x='Time', y='Users',
  	title='Simulated users over time',
  	subtitle='dotted=addressable market    dashed=unblocked users    red=active users'
    )
)

pz = p + coord_cartesian(ylim=c(0,1000))

p1a = (
  ggplot(data=rr, aes(x=t, y=users, color=strategy))
#  + geom_step(aes(y=interested), linetype=3, size=0.75)
#  + geom_step(aes(y=satisfiable), linetype=2)
  + geom_step(size=1)
#  + facet_grid(strategy~.)
#  + facet_wrap(~strategy)
  + theme_bw()
)

mra = subset(mr, metric=='active users')
mra$metric = factor(mra$metric, c('active users'))
p1b = (
  ggplot(data=mr, aes(x=t, y=value, xcolor=metric, linetype=metric))
  + geom_line()
  + geom_line(data=mra, color='red')
  + facet_grid(strategy~.)
#  + facet_wrap(~strategy)
#  + scale_y_log10()
  + theme_bw()
  + labs(x='time', y='users')
)

p2 = (
  ggplot(data=rr, aes(x=t, y=cumu, color=strategy))
  + geom_line()
#  + facet_grid(strategy~.)
#  + facet_wrap(~strategy)
  + theme_bw()
)


save = function() {
	print(p0)
	ggsave('plot0.png', width=8.7, height=3.3, dpi=75, bg='white')
	print(p)
	ggsave('plot1.png', width=8.7, height=6.6, dpi=75, bg='white')
	print(pz)
	ggsave('plot2.png', width=8.7, height=6.6, dpi=75, bg='white')
}
