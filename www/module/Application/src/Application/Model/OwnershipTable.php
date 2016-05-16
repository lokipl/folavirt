<?php

namespace Application\Model;

use Zend\Db\TableGateway\TableGateway;
use Zend\Db\Sql\Expression;
use Zend\Db\Sql\Sql;

use Application\Authentication\PAM;

class OwnershipTable
{
	protected $tablegateway;

	public function __construct(TableGateway $tableGateway)
	{
		$this -> tablegateway = $tableGateway;
	}
	
	/**
	 * Zwraca wszystkie nazwy domen użytkownika
	 * 
	 * @param Nazwa
	 * @return array
	 */
	public function getUserDomainNames($user)
	{
		$domains = array();
				
		$rows = $this -> tablegateway -> select(array('user' => $user));

		foreach ($rows as $row)
		{
			$domains[] = $row -> name;
		}
		
		$domains = array_unique($domains);
		
		return $domains;
	}
}
