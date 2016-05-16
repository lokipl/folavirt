<?php

namespace Application\Model\Folavirt\Networking;

/**
 * Odpowiedź agenta
 * 
 * @package Application\Model\Folavirt
 * @see lib/folavirt/networking/Response
 */
class Response
{
	public $command;
	public $data = array();
	public $errorcode = 0;
	
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
	 * Ustawia kod błędu
	 * 
	 * @param błąd
	 * @return void
	 */
	public function setErrorCode($error)
	{
		$this -> errorcode = $error;
	}
	
	/**
	 * Zwraca kod błędu
	 * 
	 * @param void
	 * @return błąd
	 */
	public function getErrorCode()
	{
		return $this -> errorcode;
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
		$retarray['errorcode'] = $this -> errorcode;
		
		return json_encode($retarray);
	}
	
	/**
	 * Ustawia pola na podstawie ciągu JSON
	 * 
	 * @param json
	 * @return void
	 */
	public function setFromJSON($json)
	{
		$retarray = json_decode($json, 1);
		$this -> command = $retarray['command'];
		$this -> data = $retarray['data'];
		$this -> errorcode = $retarray['errorcode'];
	}
}
