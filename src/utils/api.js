import service from "./service";


export function getDataCenters(){
    return service({
        method: 'get',
        url: `/dataCenters/getDataCenters`,
    });
}

export function getData(clusterName){
    return service({
        method: 'get',
        url: `/k8s/getData`,
        params: {
            clusterName: clusterName
        }
    });
}

export function getAllClusterInfo(cityId) {
    return service({
        method: 'get',
        url: `/cluster/getAllClusterInfo/${cityId}`,
    });
}

export function getClusterBaseInfo(selectCluster) {
    return service({
        method: 'get',
        url: `/cluster/getClusterBaseInfo/${selectCluster}`,
    });
}

export function getClusterResource(clusterName) {
    return service({
        method: 'get',
        url: `/k8s/getClusterResource/${clusterName}`,
    });
}

export function getNodeInfoByClusterName(clusterName) {
    return service({
        method: 'get',
        url: `/k8s/getNodeInfo/${clusterName}`,
    });
}

export function getClusterInfoByClusterName(clusterName) {
    return service({
        method: 'get',
        url: `/k8s/getClusterInfo/${clusterName}`,
    });
}

export function getPredictClusterInfoByClusterName(clusterName) {
    return service({
        method: 'get',
        url: `/k8s/getPredictClusterInfo/${clusterName}`,
    });
}

export function getNodeResource(clusterName) {
    return service({
        method: 'get',
        url: `/k8s/getNodeResource`,
        params: {
            clusterName: clusterName
        }
    });
}


// export function updateUserInfo(userId, data) {
//     return service({
//         method: 'get',
//         url: `/node/getNodeInfo/${userId}`,
//         data: data,
//     });
// }