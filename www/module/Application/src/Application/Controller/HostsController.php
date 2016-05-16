<?php

namespace Application\Controller;

use Zend\Mvc\Controller\AbstractActionController;
use Zend\View\Model\ViewModel;

use Application\Authentication\PAM;
use Application\Model\Folavirt\Networking\Agent;
use Application\Model\Folavirt\Remote\Pool;

/**
 * Zarządzanie hostami
 *
 * @package Application\Controller
 */
class HostsController extends AbstractActionController
{
	private $auth;
	/**
	 * Sprawdza uprawnienia
	 *
	 * @param void
	 * @return void
	 */
	private function checkRights()
	{
		// Pobiera serwis autoryzacji
		$this -> auth = $this -> getServiceLocator() -> get('PamAuth');

		if (!PAM::isPriviliged($this -> auth -> getIdentity()))
		{
			return false;
		}
		
		return true;
	}

	/**
	 * Dodaje panel boczny
	 *
	 * @param void
	 * @return void
	 */
	private function addSideBar()
	{
		// Sprawdzanie czy użytkownik jest uprzywilejowany
		$priviliged = PAM::isPriviliged($this -> auth -> getIdentity());

		// Tworzenie widoku panelu
		$sidebar = new ViewModel( array('priviliged' => $priviliged));
		$sidebar -> setTemplate('layout/sub/panel');

		// Dodawanie do głównego layoutu
		$this -> layout() -> addChild($sidebar, 'sidebar');
	}

	/**
	 * Lista zarządców
	 *
	 * @package actions
	 */
	public function indexAction()
	{
		// Sprawdza uprawnienia do maszyn wirt.
		if (!$this -> checkRights())
		{
			return $this -> redirect() -> toUrl('panel', array(
				'controller' => 'panel',
				'action' => 'index'
			));
		}
		$this -> addSideBar();

		$agents = Agent::getAgents();

		return array('agents' => $agents);
	}

	/**
	 * Wyświetlanie hosta
	 *
	 * @package actions
	 */
	public function detailsAction()
	{
		// Sprawdzanie uprawnień
		$this -> checkRights();
		$this -> addSideBar();

		// Pobieranie parametru
		$id = $this -> params() -> fromRoute('name');

		// Pobieranie agenta
		$agents = Agent::getAgents();
		$agent = $agents[$id - 1];

		return new ViewModel( array(
			'agent' => $agent,
			'id' => $id
		));
	}

	/**
	 * Wyświetla pule dyskowe
	 *
	 * @package actions
	 */
	public function poolAction()
	{
		// Sprawdzanie uprawnień
		$this -> checkRights();
		$this -> addSideBar();

		// Pobieranie parametrów
		$id = $this -> params() -> fromRoute('name');
		$pool = $this -> params() -> fromRoute('name2');

		// Pobieranie agenta
		$agents = Agent::getAgents();
		$agent = $agents[$id - 1];

		$pool = new Pool($agent, $pool);

		return new ViewModel(array('pool' => $pool));
	}

	/**
	 * Lista wszystkich maszyn wirtualnych
	 *
	 * @package actions
	 */
	public function machinesAction()
	{
		if (!$this -> checkRights())
		{
			return $this -> redirect() -> toUrl('panel', array(
				'controller' => 'panel',
				'action' => 'index'
			));
		}
		
		$this -> addSideBar();

		$agents = Agent::getAgents();

		$domains = array();
		foreach ($agents as $agent)
		{
			$domains = array_merge($domains, $agent -> getDomains());
		}

		// Sortowanie
		usort($domains, 'Application\Model\Folavirt\Remote\Domain::comparator');

		return array('domains' => $domains);
	}

	/**
	 * Aktualizuje iscsi
	 *
	 * @package actions
	 */
	public function iscsiupdateAction()
	{
		$this -> checkRights();

		$agents = Agent::getAgents();
		foreach ($agents as $agent)
		{
			$agent -> updateIscsi();
		}

		$this -> redirect() -> toRoute(null, array(
			'controller' => 'hosts',
			'action' => 'index'
		));
	}

}
