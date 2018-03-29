
<?
require_once('algoliasearch-client-php-master/algoliasearch.php');

$client = new \AlgoliaSearch\Client('QYV3TJHU9C', 'cd940c58ddb0bbfcc5538ccbcde5d112');

$index = $client->initIndex('your_index_name');

?>
