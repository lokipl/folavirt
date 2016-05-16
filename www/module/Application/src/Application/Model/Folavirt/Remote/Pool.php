<?php

namespace Application\Model\Folavirt\Remote;

use Application\Model\Folavirt\Networking\Query;

/**
 * Pula dyskowa
 * 
 * @package Application\Model\Folavirt\Remote
 */
class Pool
{
	public $agent;
	public $name;
	
	public function __construct($agent, $name)
	{
		$this -> agent = $agent;
		$this -> name = $name;
	}
	
	public function getName()
	{
		return $this -> name;
	}
	
	public function getAgent()
	{
		return $this -> agent;
	}
	
	public function getVolumes()
	{
		// Tworzenie zapytania
		$q = new Query();
		$q -> setCommand('getpoolvolumes');
		$q -> setData($this -> name);
		
		$r = $this -> getAgent() -> execute($q);
		
		return $r -> getData();
	}
	
	public function __toString()
	{
		return $this -> name;
	}
}
