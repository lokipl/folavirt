<?php

namespace Application\Model;

class Ownership
{
	public $id;
	public $name;
	public $uid;
	
	public function exchangeArray($data)
	{
		$this -> id = (!empty($data['id'])) ? $data['id'] : null;
    	$this -> name = (!empty($data['name'])) ? $data['name'] : null;
		$this -> uid = (!empty($data['uid'])) ? $data['uid'] : null;
	}
}
