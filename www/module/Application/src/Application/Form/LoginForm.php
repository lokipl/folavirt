<?php

namespace Application\Form;

use Zend\Form\Form;
use Zend\Form\Element\Text;
use Zend\Form\Element\Password;

class LoginForm extends Form
{
	public $login;
	public $password;

	public function __construct()
	{
		parent::__construct('LoginForm');

		$this -> setAttribute('method', 'post');
		$this -> setAttribute('enctype', 'multipart/form-data');

		$options = array('label_attributes' => array('class' => 'control-label col-xs-offset-1 col-xs-2'));

		// Input - login
		$this -> login = new Text('login');
		$this -> login -> setLabel('Login:');
		$this -> login -> setAttributes(array(
			'class' => 'form-control',
			'required' => true
		));
		$this -> login -> setOptions($options);

		// Dodawanie login do formy
		$this -> add($this -> login);

		// Pole - hasło
		$this -> password = new Password('password');
		$this -> password -> setLabel('Hasło:');
		$this -> password -> setAttributes(array(
			'class' => 'form-control',
			'required' => true
		));
		$this -> password -> setOptions($options);

		// Dodawanie pola hasło do formy
		$this -> add($this -> password);
	}

}
