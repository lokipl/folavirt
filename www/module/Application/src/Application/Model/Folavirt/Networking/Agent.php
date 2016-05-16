<?php

namespace Application\Model\Folavirt\Networking;

use Zend\Config\Reader\Ini;

use Application\Model\Folavirt\Remote\Domain;
use Application\Model\Folavirt\Remote\Pool;

/**
 * Połączenie z agentem
 * 
 * @package Application\Model\Folavirt
 * @see lib/folavirt/remote/RemoteObject
 */
class Agent
{
	/**
	 * Zwraca Agenta z pliku konfiguracyjnego
	 * 
	 * @param void
	 * @return Agent
	 * @static
	 */
	public static function getFromConfig()
	{
		$agents = self::getAgents();
		
		foreach ($agents as $k => $agent)
		{
			if (!$agent -> alive())
			{
				unset($agents[$k]);
			}
		}
		
		if (count($agents) == 0)
		{
			return false;
		}
		
		$agents = array_values($agents);
		
		return $agents[rand(0, count($agents)-1)];
	}
	
	/**
	 * Zwraca listę agentów
	 * 
	 * @param void
	 * @return array(Agent)
	 * @static
	 */
	public static function getAgents()
	{
		$agents = array();
		
		$lines = file('../etc/agents');
		foreach ($lines as $line)
		{
			if ($line[0] == "#") continue;

			$definition = preg_split('/\s+/', $line);

			if (count($definition) < 3)
			{
				continue;
			}
			
			$agents[] = new Agent($definition[1], intval($definition[2]), $definition[0]);
		}
		
		return $agents;
	}
	
	protected $address = null;
	protected $port = null;
	protected $name = null;
	
	public function __construct($address, $port, $name = null)
	{
		$this -> address = $address;
		$this -> port = $port;
		
		if ($name != null)
		{
			$this -> name = $name;
		}
	}
	
	/**
	 * Zwraca nazwę agenta
	 * 
	 * @param void
	 * @return nazwa
	 */
	public function getName()
	{
		return $this -> name;
	}
	
	/**
	 * Zwraca adres agenta
	 * 
	 * @param void
	 * @return adres
	 */
	public function getAddress()
	{
		return $this -> address;
	}
	
	public function getExternalAddress()
	{
		$reader = new Ini();
		$data = $reader -> fromFile('../etc/folavirt.ini');
				
		if (isset($data['vnc']['accessip'][$this -> getName()]))
		{
			return $data['vnc']['accessip'][$this -> getName()];
		}	
		else 
		{
			return $this -> getAddress();	
		}
	}
	
	/**
	 * Zwraca port agenta
	 * 
	 * @param void
	 * @return port
	 */
	public function getPort()
	{
		return $this -> port;
	}
	
	/**
	 * Sprawdza czy host odpowiada
	 * 
	 * @param void
	 * @return bool
	 */
	public function alive()
	{
		$q = new Query();
		$q -> setCommand('ping');
		
		// Wykonywanie zapytania
		try
		{
			$r = $this -> execute($q);
		}
		catch(\Exception $e)
		{
			return false;
		}
		
		// Sprawdzanie odpowiedzi
		if ($r -> getCommand() == 'pong')
		{
			return true;
		}
		
		return false;
	}
	
	/**
	 * Zwraca wszystkie domeny
	 * 
	 * @param void
	 * @return  array(Domain)
	 */
	public function getDomains()
	{
		$q = new Query();
		$q -> setCommand('vmlist');
		
		$r = $this -> execute($q);
		
		$domains = array();
		
		if (is_array($r -> getData()))
		{		
			foreach ($r -> getData() as $domaindefinition)
			{
				$domain = new Domain();
				$domain -> name = $domaindefinition['name'];
				$domain -> state = $domaindefinition['state'];
				$domain -> agent = $this;
				
				$domains[] = $domain;
			}
		}
		
		return $domains;
	}
	
	/**
	 * Zwraca pule dyskowe
	 * 
	 * @param void
	 * @return array(Pool)
	 */
	public function getPools()
	{
		$q = new Query();
		$q -> setCommand('getpools');

		$r = $this -> execute($q);
		
		$pools = array();
		
		foreach($r -> getData() as $poolname)
		{
			$pool = new Pool($this, $poolname);
			$pools[] = $pool;
		}
		
		return $pools;
	}
	
	/**
	 * Aktualizuje konfiguracje iscsi
	 * 
	 * @param void
	 * @return void
	 */
	public function updateIscsi()
	{
		$q = new Query();
		$q -> setCommand('iscsi-sync');
		
		$r = $this -> execute($q);
	}
	
	/**
	 * Wykonuje zapytanie na Agencie
	 * 
	 * @param Query
	 * @return Response
	 */
	public function execute(Query $query)
	{
		$socket = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);
		
		if (@socket_connect($socket, $this -> address, $this -> port) === false)
		{
			// Błąd połączenia
			throw new \Exception('Failed Agent connection ' . socket_strerror(socket_last_error()));
		}
			
		/*$status = socket_get_status($socket);
		var_dump($status);
		if (!is_array($status))	
		{
			throw new \Exception('Agent connection lost');
		}*/	
				
		socket_write($socket, $query -> getJSON(), strlen($query -> getJSON()));
		
		// Ustawianie timeout na odpowiedź (5 sekund)
		socket_set_option($socket, SOL_SOCKET, SO_RCVTIMEO, array("sec" => 5, "usec" => 0));

		$responsejson = socket_read($socket, 1024);
		
		$response = new Response();
		$response -> setFromJSON($responsejson);
		
		socket_write($socket, "quit\n");
		socket_close($socket);
		
		return $response;
	}
}
