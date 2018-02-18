<?php
$str = 'Node(2, 
                Node(7, 
                    Node(2, null, null),
                    Node(6, 
                        Node(5, null, null), 
                        Node(8, null, null))
                    ),
                Node(5,
                    null,
                    Node(9, 
                        null,
                        Node(2, null, null)
                        )
                    )
            )';
            

$str = '$ar = '.str_replace('Node', 'array', $str).';';

eval($str);
$globalSave = [];
searchSum($ar, [], 11, $globalSave);

foreach($globalSave as $z)
{
    echo implode(' -> ', $z).'<br>';
}

function searchSum($ar, $arNum, $count, &$globalSave)
{
    $arNum[] = $ar[0];

    do
    {
        $sum = array_sum($arNum);
        
        if($sum == $count)
        {
            $globalSave[] = $arNum;
        }
        
        if($sum > $count || ($sum == $count))
        {
            reset($arNum);
            unset($arNum[key($arNum)]);    
        }
    }
    while($sum > $count);

    for($i = 1; $i < 3; $i++)
    {
        if(is_array($ar[$i]))
        {
            searchSum($ar[$i], $arNum, $count, $globalSave);    
        }    
    }
}
