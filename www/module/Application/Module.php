<?php

namespace Application;

use Zend\ModuleManager\Feature\AutoloaderProviderInterface;
use Zend\Mvc\ModuleRouteListener;
use Zend\Mvc\MvcEvent;
use Zend\Authentication\Storage;
use Zend\Authentication\AuthenticationService;
use Zend\Db\TableGateway\TableGateway;
use Zend\Db\ResultSet\ResultSet;
use Zend\Config\Reader\Ini;

use Application\Authentication\PAM;
use Application\Authentication\Imap;

use Application\Model\Ownership;
use Application\Model\OwnershipTable;

class Module implements AutoloaderProviderInterface
{
	public function onBootstrap(MvcEvent $e)
	{
		$eventManager = $e -> getApplication() -> getEventManager();
		$moduleRouteListener = new ModuleRouteListener();
		$moduleRouteListener -> attach($eventManager);
	}

	public function getConfig()
	{
		// Odczytywanie konfiguracji bazy danych
		$reader = new Ini();
		$data = $reader -> fromFile('../etc/folavirt.ini');
		$db = $data['database'];
			
		$arr = include __DIR__ . '/config/module.config.php';
		
		$arr['db'] = array(
			'driver' => 'Pdo',
				'dsn' => 'mysql:dbname=' . $db['db'] . ';host=' . $db['host'],
				'username' => $db['user'],
				'password' => $db['passwd'],
				'driver_options' => array(\PDO::MYSQL_ATTR_INIT_COMMAND => 'SET NAMES \'UTF8\''),
				'prefix' => $db['prefix'],
		);

		return $arr;
	}

	public function getAutoloaderConfig()
	{
		return array('Zend\Loader\StandardAutoloader' => array('namespaces' => array(__NAMESPACE__ => __DIR__ . '/src/' . __NAMESPACE__, ), ), );
	}

	/**
	 * Services
	 *
	 * @param void
	 * @return  array
	 */
	public function getServiceConfig()
	{
		// Konfiguracja bazy danych
		$reader = new Ini();
		$data = $reader -> fromFile('../etc/folavirt.ini');
		
		define("DB_PREFIX", $data['database']['prefix']);
		
		return array(
			'factories' => array(
				// Autoryzacja
				'PamAuth' => function($sm)
				{
					$authservice = new AuthenticationService();
					$authservice -> setAdapter(new PAM());
					$authservice -> setStorage(new Storage\Session());

					return $authservice;
				},
				'ImapAuth' => function($sm)
				{
					$imapauthservice = new AuthenticationService();
					$imapauthservice -> setAdapter(new Imap());
					$imapauthservice -> setStorage(new Storage\Session());
					
					return $imapauthservice;
				},
				// Tabela własności maszyn wirtualnych
				'Model/OwnershipTable' => function($sm)
				{
					$db = $sm -> get('Zend\Db\Adapter\Adapter');
					$resultset = new ResultSet();
					$resultset -> setArrayObjectPrototype(new Ownership());

					$tg = new TableGateway(DB_PREFIX.'ownership', $db, null, $resultset);

					return new OwnershipTable($tg);
				},
			),
		);
	}

}
