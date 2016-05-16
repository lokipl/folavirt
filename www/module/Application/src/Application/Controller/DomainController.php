<?php

namespace Application\Controller;

use Zend\Mvc\Controller\AbstractActionController;
use Zend\View\Model\ViewModel;
use Zend\Form\Annotation\AnnotationBuilder;
use Zend\Config\Reader\Ini;

use Application\Authentication\PAM;
use Application\Model\Folavirt\Remote\Domain;
use Application\Form\VncPassword;

/**
 * Domena
 *
 * @package Application\Controller
 */
class DomainController extends AbstractActionController
{
	private $auth;
	private $name;
	/**
	 * Pobiera z parametru nazwę domeny oraz sprawdza uprawnienia użytkownika do domeny
	 *
	 * @param void
	 * @return void
	 */
	private function getDomainAndCheckRights()
	{
		$this -> auth = $this -> getServiceLocator() -> get('PamAuth');

		if (!$this -> auth -> hasIdentity())
		{
			return 1;
		}

		$this -> name = $this -> params() -> fromRoute('name');

		if (PAM::isPriviliged($this -> auth -> getIdentity()))
		{
			return 0;
		}

		$ownership = $this -> getServiceLocator() -> get('Model/OwnershipTable');
		$domains = $ownership -> getUserDomainNames($this -> auth -> getIdentity());
		if (!in_array($this -> name, $domains))
		{
			return 2;
		}

		return 0;
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
			$sidebar = new ViewModel( array('priviliged' => $priviliged));
			$sidebar -> setTemplate('layout/sub/panel');

			$this -> layout() -> addChild($sidebar, 'sidebar');
		}
	}

	public function handlenextstep()
	{
		if (isset($_GET['back']))
		{
			if ($_GET['back'] == 'domain')
			{
				return $this -> redirect() -> toRoute('domain', array(
					'controller' => 'Domain',
					'action' => 'details',
					'name' => $this -> name
				));
			}
			if ($_GET['back'] == 'alldomains')
			{
				return $this -> redirect() -> toRoute('hosts', array(
					'controller' => 'Hosts',
					'action' => 'machines',
				));
			}
		}
		return $this -> redirect() -> toRoute('panel', array(
			'controller' => 'panel',
			'action' => 'index'
		));
	}

	private function getPageConfig()
	{
		$reader = new Ini();
		$data = $reader -> fromFile('../etc/folavirt.ini');
		return $data['www'];
	}

	/**
	 * Szczegóły maszyny wirtualnej
	 *
	 * @package actions
	 */
	public function detailsAction()
	{
		$out = $this -> getDomainAndCheckRights();

		if ($out == 1)
		{
			return $this -> redirect() -> toRoute('panel', array(
				'controller' => 'panel',
				'action' => 'index'
			));
		}

		if ($out == 2)
		{
			return $this -> redirect() -> toRoute('panel', array(
				'controller' => 'panel',
				'action' => 'index'
			));
		}

		$this -> addSideBar();

		try
		{
			$domain = new Domain($this -> name);
			$domain -> lookForAgent();

			$vncpassword = new VncPassword();
			$builder = new AnnotationBuilder();
			$vncform = $builder -> createForm($vncpassword);

			return array(
				'domain' => $domain,
				'vncform' => $vncform,
				'config' => $this -> getPageConfig()
			);
		}
		catch(\Exception $e)
		{
			return $this -> redirect() -> toRoute('panel', array(
				'controller' => 'panel',
				'action' => 'index'
			));
		}
	}

	/**
	 * Zmiana hasła VNC
	 *
	 * @param void
	 * @return void
	 */
	public function changevncpasswdAction()
	{
		$out = $this -> getDomainAndCheckRights();

		if ($out == 1)
		{
			return $this -> redirect() -> toRoute('panel', array(
				'controller' => 'panel',
				'action' => 'index'
			));
		}

		if ($out == 2)
		{
			return $this -> redirect() -> toRoute('panel', array(
				'controller' => 'panel',
				'action' => 'index'
			));
		}

		$vncpassword = new VncPassword();
		$builder = new AnnotationBuilder();
		$form = $builder -> createForm($vncpassword);

		if ($this -> getRequest() -> isPost())
		{
			$form -> bind($vncpassword);
			$form -> setData($this -> getRequest() -> getPost());
			if ($form -> isValid())
			{
				$data = $form -> getData();
				$newpasswd = $data -> password;

				$domain = new Domain($this -> name);

				try
				{
					$domain -> lookForAgent();
				}
				catch(\Exception $e)
				{
					return $this -> redirect() -> toRoute('panel', array(
						'controller' => 'panel',
						'action' => 'index'
					));
				}

				$domain -> clearGraphicConsoleTemporaryPasswd();
				$domain -> setGraphicConsolePasswd($data -> password);

				return $this -> handlenextstep();
			}
		}

	}

	/**
	 * Uruchomienie maszyny wirtualnej
	 *
	 * @package actions
	 */
	public function startAction()
	{
		$out = $this -> getDomainAndCheckRights();

		if ($out == 1)
		{
			return $this -> redirect() -> toRoute('panel', array(
				'controller' => 'panel',
				'action' => 'index'
			));
		}

		if ($out == 2)
		{
			return $this -> redirect() -> toRoute('panel', array(
				'controller' => 'panel',
				'action' => 'index'
			));
		}

		$domain = new Domain($this -> name);

		try
		{
			$domain -> lookForAgent();
		}
		catch(\Exception $e)
		{
			return $this -> redirect() -> toRoute('panel', array(
				'controller' => 'panel',
				'action' => 'index'
			));
		}

		$domain -> start();

		return $this -> handlenextstep();
	}

	/**
	 * Zatrzymanie maszyny wirtualnej
	 *
	 * @package actions
	 */
	public function destroyAction()
	{
		$out = $this -> getDomainAndCheckRights();

		if ($out == 1)
		{
			return $this -> redirect() -> toRoute('panel', array(
				'controller' => 'panel',
				'action' => 'index'
			));
		}

		if ($out == 2)
		{
			return $this -> redirect() -> toRoute('panel', array(
				'controller' => 'panel',
				'action' => 'index'
			));
		}

		$domain = new Domain($this -> name);

		try
		{
			$domain -> lookForAgent();
		}
		catch(\Exception $e)
		{
			return $this -> redirect() -> toRoute('panel', array(
				'controller' => 'panel',
				'action' => 'index'
			));
		}

		$domain -> destroy();

		return $this -> handlenextstep();
	}

	/**
	 * Wstrzymanie maszyny wirtualnej
	 *
	 * @package actions
	 */
	public function suspendAction()
	{
		$out = $this -> getDomainAndCheckRights();

		if ($out == 1)
		{
			return $this -> redirect() -> toRoute('panel', array(
				'controller' => 'panel',
				'action' => 'index'
			));
		}

		if ($out == 2)
		{
			return $this -> redirect() -> toRoute('panel', array(
				'controller' => 'panel',
				'action' => 'index'
			));
		}

		$domain = new Domain($this -> name);

		try
		{
			$domain -> lookForAgent();
		}
		catch(\Exception $e)
		{
			return $this -> redirect() -> toRoute('panel', array(
				'controller' => 'panel',
				'action' => 'index'
			));
		}

		$domain -> suspend();

		return $this -> handlenextstep();
	}

	/**
	 * Wznowienie maszyny wirtualnej
	 *
	 * @package actions
	 */
	public function resumeAction()
	{
		$out = $this -> getDomainAndCheckRights();

		if ($out == 1)
		{
			return $this -> redirect() -> toRoute('panel', array(
				'controller' => 'panel',
				'action' => 'index'
			));
		}

		if ($out == 2)
		{
			return $this -> redirect() -> toRoute('panel', array(
				'controller' => 'panel',
				'action' => 'index'
			));
		}

		$domain = new Domain($this -> name);

		try
		{
			$domain -> lookForAgent();
		}
		catch(\Exception $e)
		{
			return $this -> redirect() -> toRoute('panel', array(
				'controller' => 'panel',
				'action' => 'index'
			));
		}

		$domain -> resume();

		return $this -> handlenextstep();
	}

	/**
	 * Wznowienie maszyny wirtualnej
	 *
	 * @package actions
	 */
	public function resetAction()
	{
		$out = $this -> getDomainAndCheckRights();

		if ($out == 1)
		{
			return $this -> redirect() -> toRoute('panel', array(
				'controller' => 'panel',
				'action' => 'index'
			));
		}

		if ($out == 2)
		{
			return $this -> redirect() -> toRoute('panel', array(
				'controller' => 'panel',
				'action' => 'index'
			));
		}

		$domain = new Domain($this -> name);

		try
		{
			$domain -> lookForAgent();
		}
		catch(\Exception $e)
		{
			return $this -> redirect() -> toRoute('panel', array(
				'controller' => 'panel',
				'action' => 'index'
			));
		}

		$domain -> reset();

		return $this -> handlenextstep();
	}

}
