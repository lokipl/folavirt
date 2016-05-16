<?php

namespace Application\Authentication;

use Zend\Config\Reader\Ini;
use Zend\Authentication\Adapter\AdapterInterface;
use Zend\Authentication\Result;

class Imap implements AdapterInterface
{
	public $identity;
	public $password;
	
	public function setIdentity($identity)
	{
		$this -> identity = $identity;
	}
	
	public function getIdentity()
	{
		return $this -> identity;
	}
	
	public function setCredential($credential)
	{
		$this -> password = $credential;
	}
	
	public function authenticate()
	{
		$reader = new Ini();
		$data = $reader -> fromFile('../etc/folavirt.ini');

		if ($mbox = imap_open($data['imapauth']['mailbox'], $this -> identity, $this -> password, null, 1))
		{
			imap_close($mbox);
			
			return Result::SUCCESS;
		}
		else
		{
			imap_errors();
			imap_alerts();
			return Result::FAILURE_UNCATEGORIZED;	
		}
	}
}
