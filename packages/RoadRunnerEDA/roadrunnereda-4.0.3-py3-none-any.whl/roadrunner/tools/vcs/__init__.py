####    ############
####    ############
####
####
############    ####
############    ####
####    ####    ####
####    ####    ####
############
############

from roadrunner.help import HelpItem
from roadrunner.tools.vcs import common, vcsSim

NAME = common.NAME
HelpItem("tool", NAME, "Synopsys VCS")

cmd_sim = vcsSim.cmd_sim