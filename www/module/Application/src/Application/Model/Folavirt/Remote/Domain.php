<?php

namespace Application\Model\Folavirt\Remote;

use Application\Model\Folavirt\Networking\Query;
use Application\Model\Folavirt\Networking\Agent;

/**
 * Domena
 *
 * @package Application\Model\Folavirt\Remote
 */
class Domain
{
	const DOMAIN_NOSTATE = 0;
	const DOMAIN_RUNNING = 1;
	const DOMAIN_BLOCKED = 2;
	const DOMAIN_PAUSED = 3;
	const DOMAIN_SHUTDOWN = 4;
	const DOMAIN_SHUTOFF = 5;
	const DOMAIN_CRASHED = 6;
	const DOMAIN_PMSUSPENDED = 7;
	const DOMAIN_LAST = 8;
	const DOMAIN_DONTEXIST = 20;

	public $name;
	public $state = -1;
	public $agent;

	public static function comparator(Domain $domain1, Domain $domain2)
	{
		return strcmp($domain1 -> getName(), $domain2 -> getName());
	}

	public function __construct($name = null)
	{
		if ($name != null)
		{
			$this -> name = $name;
		}
	}

	/**
	 * Zwraca nazwę domeny
	 *
	 * @param void
	 * @return nazwa
	 */
	public function getName()
	{
		return $this -> name;
	}

	/**
	 * Zwraca status domeny
	 *
	 * @param void
	 * @return nazwa
	 */
	public function getState()
	{
		if ($this -> state == -1)
		{
			$this -> lookForAgent();
			// Sprawdzanie statusu
			$q = new Query();
			$q -> setCommand('getstate');
			$q -> setData($this -> name);
			
			$r = $this -> getAgent() -> execute($q);
			
			$this -> state = $r -> getData();
		}
		
		return $this -> state;
	}

	/**
	 * Zwraca agenta
	 *
	 * @param void
	 * @return Agent
	 */
	public function getAgent()
	{
		return $this -> agent;
	}

	/**
	 * Szuka domeny na agencie
	 *
	 * @param void
	 * @return Agent
	 */
	public function searchAgent()
	{
		$agents = Agent::getAgents();
		foreach ($agents as $agent)
		{
			if ($agent -> alive())
			{
				foreach ($agent -> getDomains() as $domain)
				{
					if ($domain -> getName() == $this -> name)
					{
						$this -> agent = $agent;
						break;
					}
				}
			}
		}

		return $this -> agent;
	}

	/**
	 * Sprawdza czy jest zdefiniowany agent jeśli nie to go szuka
	 *
	 * @param void
	 * @return void
	 * @throws Exception
	 * @access private
	 */
	public function lookForAgent()
	{
		if ($this -> agent == null)
		{
			$this -> searchAgent();
		}

		if ($this -> agent == null)
		{
			throw new \Exception('Cant found agent');
		}
	}

	/**
	 * Opcje konsoli graficznej
	 *
	 * @param void
	 *
	 */
	public function getGraphicConsoleOptions()
	{
		// Szuka agenta
		$this -> lookForAgent();

		// Tworzenie zapytania pytającego o opcje domeny
		$q = new Query();
		$q -> setCommand('graphicconsoleoptions');
		$q -> setData($this -> name);

		$r = $this -> getAgent() -> execute($q);
		
		return $r -> getData();
	}

	/**
	 * Zwraca tymczasowe hasło dostepu do konsoli VNC
	 * 
	 * @param void
	 * @return passwd|null
	 */
	public function getTemporaryPassword()
	{
		// Szuka agenta
		$this -> lookForAgent();

		// Tworzenie zapytania pytającego o opcje domeny
		$q = new Query();
		$q -> setCommand('gettemporarypasswd');
		$q -> setData($this -> name);

		$r = $this -> getAgent() -> execute($q);
		
		return $r -> getData();
	}

	/**
	 * Ustawia adres na jakim ma słuchać konsola graficzna
	 *
	 * @param void
	 * @return void
	 */
	public function setGraphicConsoleAddress($address)
	{
		$this -> lookForAgent();

		$q = new Query();
		$q -> setCommand('setgraphicconsoleaddress');
		$q -> setData(array(
			'domain' => $this -> name,
			'address' => $address
		));

		$r = $this -> getAgent() -> execute($q);
	}

	/**
	 * Usuwa hasło do konsoli VNC
	 * 
	 * @param void
	 * @return void
	 */
	public function clearGraphicConsoleTemporaryPasswd()
	{
		$this -> lookForAgent();
		
		$q = new Query();
		$q -> setCommand('removetemporarypasswd');
		$q -> setData($this -> name);
		
		return $this -> getAgent() -> execute($q);
	}
	
	/**
	 * Ustawia hasło do konsoli graficznej
	 * 
	 * @param Hasło
	 * @return void
	 */
	public function setGraphicConsolePasswd($passwd)
	{
		$this -> lookForAgent();
		
		$q = new Query();
		$q -> setCommand('setgraphicconsolepasswd');
		$q -> setData(array('domain' => $this -> name, 'passwd' => $passwd));

		return $this -> getAgent() -> execute($q);
	}

	/**
	 * Uruchomienie maszyny wirtualnej
	 *
	 * @param void
	 * @return void
	 */
	public function start()
	{
		$this -> lookForAgent();

		$q = new Query();
		$q -> setCommand('start');
		$q -> setData($this -> name);

		return $this -> agent -> execute($q);
	}

	/**
	 * Zatrzymanie maszyny wirtualnej
	 *
	 * @param void
	 * @return void
	 */
	public function destroy()
	{
		$this -> lookForAgent();

		$q = new Query();
		$q -> setCommand('destroy');
		$q -> setData($this -> name);

		return $this -> agent -> execute($q);
	}

	/**
	 * Zatrzymanie maszyny wirtualnej
	 *
	 * @param void
	 * @return void
	 */
	public function suspend()
	{
		$this -> lookForAgent();

		$q = new Query();
		$q -> setCommand('suspend');
		$q -> setData($this -> name);

		return $this -> agent -> execute($q);
	}

	/**
	 * Wznawia maszynę wirtualną
	 *
	 * @param void
	 * @return void
	 */
	public function resume()
	{
		$this -> lookForAgent();

		$q = new Query();
		$q -> setCommand('resume');
		$q -> setData($this -> name);

		return $this -> agent -> execute($q);
	}

	/**
	 * Resetuje maszynę wirtualną
	 *
	 * @param void
	 * @return void
	 */
	public function reset()
	{
		$this -> lookForAgent();

		$q = new Query();
		$q -> setCommand('reset');
		$q -> setData($this -> name);

		return $this -> agent -> execute($q);
	}

}
