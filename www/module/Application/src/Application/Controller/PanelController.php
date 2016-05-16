<?php

namespace Application\Controller;

use Zend\Mvc\Controller\AbstractActionController;
use Zend\View\Model\ViewModel;

use Application\Model\Folavirt\Networking\Query;
use Application\Model\Folavirt\Networking\Agent;
use Application\Model\Folavirt\Remote\Domain;
use Application\Authentication\PAM;

/**
 * Panel użytkownika
 *
 * @package FolavirtWeb\Controller
 */
class PanelController extends AbstractActionController
{
	private $auth = null;

	/**
	 * Sprawdza czy jest użytkownik jest zalogowany, jeśli nie przekierowywuje do logowania
	 *
	 * @param void
	 * @return void
	 */
	private function setAuthRequired()
	{
		$this -> auth = $this -> getServiceLocator() -> get('PamAuth');

		if (!$this -> auth -> hasIdentity())
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
		$priviliged = PAM::isPriviliged($this -> auth -> getIdentity());
		
		if ($priviliged)
		{
			$sidebar = new ViewModel(array('priviliged' => $priviliged));
			$sidebar -> setTemplate('layout/sub/panel');
	
			$this -> layout() -> addChild($sidebar, 'sidebar');
		}
	}

	/**
	 * Lista maszyn wirtualnych
	 *
	 * @package actions
	 */
	public function indexAction()
	{
		if (!$this -> setAuthRequired())
		{
			return $this -> redirect() -> toRoute('login', array(
				'controller' => 'login',
				'action' => 'index'
			));
		}

		$this -> addSideBar();

		$q = new Query();
		$q -> setCommand('ownership-list-withstatuses');
		$q -> setData($this -> auth -> getIdentity());

		$agent = Agent::getFromConfig();
		if ($agent == false)
		{
			return array('agenterror' => true);
		}
		
		$response = $agent -> execute($q);

		if ($response -> getErrorCode() == 0)
		{
			$domains = array();
			foreach ($response -> getData() as $definition)
			{
				$domain = new Domain();
				$domain -> name = $definition['name'];
				$domain -> state = $definition['state'];

				$domains[] = $domain;
			}
		}

		return array('domains' => $domains);
	}

}
