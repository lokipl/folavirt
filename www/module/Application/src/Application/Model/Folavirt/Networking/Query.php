<?php

namespace Application\Model\Folavirt\Networking;

/**
 * Zapytanie do agenta folavirt
 * 
 * @package Model\Folavirt
 * @see lib/folavirt/networking/Query
 */
class Query
{
	public $command;
	public $data = array();
	
	/**
	 * Ustawia polecenie
	 * 
	 * @param string
	 * @return void
	 */
	public function setCommand($command)
	{
		$this -> command = $command;
	}
	
	/**
	 * Zwraca polecenie
	 * 
	 * @param void
	 * @return string
	 */
	public function getCommand()
	{
		return $this -> command;
	}
	
	/**
	 * Ustawia parametry
	 * 
	 * @param array
	 * @return void
	 */
	public function setData($data)
	{
		$this -> data = $data;
	}
	
	/**
	 * Zwraca parametry
	 * 
	 * @param void
	 * @return array
	 */
	public function getData()
	{
		return $this -> data;
	}
	
	/**
	 * Zwraca zapytania w formacie JSON
	 * 
	 * @param void
	 * @return json
	 */
	public function getJSON()
	{
		$retarray = array();
		$retarray['command'] = $this -> command;
		$retarray['data'] = $this -> data;
		
		return json_encode($retarray);
	}
	
	
}
