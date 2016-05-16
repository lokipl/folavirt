<?php

namespace Application\Authentication;

use Zend\Authentication\Adapter\AdapterInterface;
use Zend\Authentication\Result;

/**
 * Adapter autoryzacji za pomocą PAM
 * 
 * @package Authentication
 * @see http://pecl.php.net/package/PAM
 */
class PAM implements AdapterInterface
{
	/**
	 * Zwraca uid użytkownika
	 * 
	 * @param void
	 * @return uid
	 * @static
	 * @see posix_getpwnam
	 */
	public static function getUid($login)
	{
		$arr = posix_getpwnam($login);
		return $arr['uid'];
	}
	
	/**
	 * Sprawdza czy login ma podwyższony dostęp
	 * 
	 * @param login
	 * @return bool
	 */
	public static function isPriviliged($login)
	{
		$users = array('root');
		
		if (in_array($login, $users))
		{
			return true;
		}
		else 
		{
			return false;	
		}
	}
	
	private $login;
	private $password;

	/**
	 * Ustawia login
	 * 
	 * @param login
	 * @return void
	 */
	public function setIdentity($login)
	{
		$this -> login = $login;
	}
	
	/**
	 * Zwraca login użytkownika
	 * 
	 * @param void
	 * @return login
	 */
	public function getIdentity()
	{
		return $this -> login;
	}
		
	/**
	 * Ustawia hasło
	 * 
	 * @param hasło
	 * @return void
	 */
	public function setCredential($password)
	{
		$this -> password = $password;
	}
	
	/**
	 * Właściwa autoryzacja
	 * 
	 * @param void
	 * @return Result
	 */
	public function authenticate()
	{
		if (!function_exists("pam_auth")) return Result::FAILURE_UNCATEGORIZED;
		
		$error = '';
		$pamauth = pam_auth($this -> login, $this -> password, $error);
		
		if ($pamauth)
		{
			return Result::SUCCESS;
		}
		else 
		{
			return Result::FAILURE_UNCATEGORIZED;	
		}
	}
}
