#!/bin/bash
_folavirt()
{
	local cur
	local prev
	local opts
	
	cur="${COMP_WORDS[COMP_CWORD]}"
	prev="${COMP_WORDS[COMP_CWORD-1]}"
	
	opt_folavirt="create console destroy details disk dumpxml lab list migratexml ownership reset resume undefine undefine-snapshot"
	opt_agent="discover list pool"
	opt_pool="add list sync"
	opt_disk="discover list lv"
	opt_lv="list"
	opt_lab="create list remove"
	opt_ownership="list delete clean"
	
	variablename=opt_$prev
	opts=${!variablename}
	
	COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
	return 0
}

_foladisk()
{
	local cur
	local prev
	local opts
	
	cur="${COMP_WORDS[COMP_CWORD]}"
	prev="${COMP_WORDS[COMP_CWORD-1]}"
	
	opt_foladisk="iscsi lv snapshot vg"
	opt_iscsi="dump options relaod write"
	opt_options="iqnbasename iqndate iqnhostname"
	opt_lv="attach create detach list remove"
	opt_snapshot="attach create detach list remove removeall"
	opt_vg="attach detach details list"
	
	variablename=opt_$prev
	opts=${!variablename}
	
	COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
	return 0
}

complete -F _folavirt folavirt
complete -F _foladisk foladisk