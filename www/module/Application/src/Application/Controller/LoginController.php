<?php

namespace Application\Controller;

use Zend\Mvc\Controller\AbstractActionController;
use Zend\View\Model\ViewModel;
use Zend\Authentication\Storage\Session;
use Zend\Authentication\Result;

use Application\Form\LoginForm;
use Application\Authentication\PAM;

/**
 * Kontroler logowania
 *
 * @package FolavirtWeb\Controller
 */
class LoginController extends AbstractActionController
{
	/**
	 * Formularz logowania
	 *
	 * @package actions
	 */
	public function indexAction()
	{
		$auth = $this -> getServiceLocator() -> get('PamAuth');
		if ($auth -> hasIdentity()) return $this -> redirect() -> toRoute('panel', array(
			'controller' => 'panel',
			'action' => 'index'
		));

		$this -> layout() -> setVariable('needlogin', true);

		return array('form' => new LoginForm());
	}

	/**
	 * Akacja logowania użytkownika
	 *
	 * @package actions
	 */
	public function processAction()
	{
		$form = new LoginForm();

		if ($this -> getRequest() -> isPost())
		{
			$form -> setData($this -> getRequest() -> getPost());

			if ($form -> isValid())
			{
				$imap = $this -> getServiceLocator() -> get('ImapAuth');
				$imap -> getAdapter() -> setIdentity($this -> getRequest() -> getPost('login'));
				$imap -> getAdapter() -> setCredential($this -> getRequest() -> getPost('password'));

				// Najpierw autoryzacja via imap
				$result = $imap -> getAdapter() -> authenticate();
				if ($result == Result::SUCCESS)
				{
					$imap -> getStorage() -> write($imap -> getAdapter() -> getIdentity());
					
					return $this -> redirect() -> toRoute('panel', array(
						'controller' => 'panel',
						'action' => 'index'
					));
				}

				$pam = $this -> getServiceLocator() -> get('PamAuth');
				$pam -> getAdapter() -> setIdentity($this -> getRequest() -> getPost('login'));
				$pam -> getAdapter() -> setCredential($this -> getRequest() -> getPost('password'));

				// Autoryzacja via PAM
				$result = $pam -> getAdapter() -> authenticate();
				if ($result == Result::SUCCESS)
				{
					$pam -> getStorage() -> write($pam -> getAdapter() -> getIdentity());
					
					return $this -> redirect() -> toRoute('panel', array(
						'controller' => 'panel',
						'action' => 'index'
					));
				}

				$vm = new ViewModel( array(
					'status' => 'failure',
					'form' => $form
				));
				$vm -> setTemplate('application/login/index');

				return $vm;
			}
		}
		else
		{
			$this -> redirect() -> toRoute(null, array(
				'controller' => 'login',
				'action' => 'index'
			));
		}
	}

	/**
	 * Akacja wylogowania użytownika
	 *
	 * @package actions
	 */
	public function logoutAction()
	{
		$auth = $this -> getServiceLocator() -> get('PamAuth');
		$auth -> clearIdentity();

		return $this -> redirect() -> toRoute(null, array(
			'controller' => 'login',
			'action' => 'index'
		));
	}

}
